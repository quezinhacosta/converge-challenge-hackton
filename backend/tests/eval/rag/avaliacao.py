"""Avaliacao reproduzivel do RAG documental (recuperacao + fundamentacao).

Uso (a partir de backend/):
    python -m tests.eval.rag.avaliacao --split dev
    python -m tests.eval.rag.avaliacao --split validacao --saida resultados/
    python -m tests.eval.rag.avaliacao --split dev --llm     # gasta creditos Featherless

Checagens deterministicas (sem rede): acerto da recuperacao, abstencao sem evidencia,
vazamento (outra empresa, rascunho, excluido, vencido, versao substituida), marcacao de
injecao, e robustez da validacao contra um gerador adversario (ref inventada, numero
inventado). Com --llm, as respostas reais vao para a revisao humana (RUBRICA.md).
O manifesto registra hashes do corpus e das perguntas, versao do prompt, modelo e config.
"""

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from app.knowledge.domain import ContextoAutorizado
from app.knowledge.dtos import (
    CadastroTextoRequest,
    ConsultaRecuperacao,
    NovaVersaoTextoRequest,
    PerguntaRequest,
    ResultadoRecuperacao,
)
from app.knowledge.grounding import PROMPT_SISTEMA, GeradorTexto, RespondedorFundamentado
from app.knowledge.repository import (
    ArmazenamentoOriginalEmMemoria,
    RepositorioConhecimentoEmMemoria,
)
from app.knowledge.retrieval import RecuperadorTextual
from app.knowledge.service import ServicoConhecimento
from tests.eval.rag.corpus import CORPUS, DIA_REFERENCIA, por_chave

AQUI = Path(__file__).resolve().parent
ARQUIVO_PERGUNTAS = AQUI / "perguntas.jsonl"
EMPRESAS = {
    "AURORA": UUID("aaaaaaaa-0000-4000-8000-000000000001"),
    "BRISA": UUID("bbbbbbbb-0000-4000-8000-000000000002"),
}
USUARIO = UUID("cccccccc-0000-4000-8000-000000000003")
VERSAO_AVALIACAO = "rag-eval-v1"

# Resposta adversaria: cita um trecho que existe, inventa um numero e cita ref inexistente.
RESPOSTA_ADVERSARIA = (
    "Segundo a politica, cada colaborador tem 99 sessoes por ano [C1]. "
    "A empresa cumpre integralmente a NR-1 [C9]."
)


def ctx(empresa: str) -> ContextoAutorizado:
    return ContextoAutorizado(
        EMPRESAS[empresa], USUARIO, frozenset({"RH"}), frozenset({"RH"}), "eval"
    )


def sha256(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


@dataclass
class Pergunta:
    id: str
    split: str
    empresa: str
    tipo: str
    pergunta: str
    esperados: list[str] = field(default_factory=list)
    proibidos: list[str] = field(default_factory=list)
    termos_proibidos: list[str] = field(default_factory=list)
    insuficiente: bool | None = None
    fator: str | None = None


def carregar_perguntas(split: str | None = None) -> list[Pergunta]:
    linhas = ARQUIVO_PERGUNTAS.read_text(encoding="utf-8").splitlines()
    todas = [Pergunta(**json.loads(linha)) for linha in linhas if linha.strip()]
    return [p for p in todas if split in (None, "todos") or p.split == split]


def hash_split(split: str) -> str:
    """Hash estavel das perguntas de um split (detecta edicao do conjunto congelado)."""
    linhas = [
        json.dumps(asdict(p), sort_keys=True, ensure_ascii=False) for p in carregar_perguntas(split)
    ]
    return sha256("\n".join(linhas))


# -- ambiente ------------------------------------------------------------------------------


@dataclass
class AmbienteAvaliacao:
    repo: RepositorioConhecimentoEmMemoria
    servico: ServicoConhecimento
    recuperador: RecuperadorTextual
    ids: dict[str, UUID]  # chave do corpus -> documento_id

    def chave_de(self, documento_id: UUID) -> str:
        return next(k for k, v in self.ids.items() if v == documento_id)


def montar_ambiente() -> AmbienteAvaliacao:
    repo = RepositorioConhecimentoEmMemoria()
    servico = ServicoConhecimento(
        repo, ArmazenamentoOriginalEmMemoria(), lambda: datetime(2026, 11, 1, 12, tzinfo=UTC)
    )
    ids: dict[str, UUID] = {}
    for doc in CORPUS:
        c = ctx(doc.empresa)
        primeira, *seguintes = doc.versoes
        criado = servico.cadastrar_texto(
            c,
            CadastroTextoRequest(
                titulo=doc.titulo,
                categoria=doc.categoria,
                responsavel="RH (avaliacao)",
                texto=primeira.texto,
                vigencia_inicio=primeira.vigencia_inicio,
                vigencia_fim=primeira.vigencia_fim,
                confirma_sem_dados_sensiveis=True,
            ),
        )
        for v in seguintes:
            criado = servico.adicionar_versao_texto(
                c,
                criado.id,
                NovaVersaoTextoRequest(
                    texto=v.texto,
                    vigencia_inicio=v.vigencia_inicio,
                    vigencia_fim=v.vigencia_fim,
                    confirma_sem_dados_sensiveis=True,
                ),
            )
        ids[doc.chave] = criado.id
        if doc.destino == "RASCUNHO":
            continue
        servico.publicar(c, criado.versoes[-1].id)
        if doc.destino == "EXCLUIDO":
            servico.excluir(c, criado.id)
    return AmbienteAvaliacao(repo, servico, RecuperadorTextual(repo), ids)


# -- avaliacao por pergunta ----------------------------------------------------------------


@dataclass
class ResultadoPergunta:
    id: str
    tipo: str
    empresa: str
    recuperados: list[str]
    evidencia_suficiente: bool
    acerto: bool | None = None  # algum esperado entre os recuperados
    posicao: int | None = None  # posicao (1..k) do primeiro esperado
    abstencao_ok: bool | None = None
    vazamentos: list[str] = field(default_factory=list)
    injecao_nao_marcada: list[str] = field(default_factory=list)
    adversario_ok: bool | None = None
    resposta_llm: str | None = None
    citacoes_llm: list[str] = field(default_factory=list)


def _checar_recuperacao(
    amb: AmbienteAvaliacao, p: Pergunta, r: ResultadoRecuperacao
) -> ResultadoPergunta:
    chaves = [amb.chave_de(t.documento_id) for t in r.trechos]
    res = ResultadoPergunta(p.id, p.tipo, p.empresa, chaves, r.evidencia_suficiente)
    if p.esperados:
        posicoes = [i for i, k in enumerate(chaves, start=1) if k in p.esperados]
        res.acerto = bool(posicoes)
        res.posicao = posicoes[0] if posicoes else None
    if p.insuficiente is not None:
        res.abstencao_ok = r.evidencia_suficiente is (not p.insuficiente)
    for chave, trecho in zip(chaves, r.trechos, strict=True):
        doc = por_chave(chave)
        if doc.empresa != p.empresa:
            res.vazamentos.append(f"{chave}:OUTRA_EMPRESA")
        if chave in p.proibidos:
            res.vazamentos.append(f"{chave}:PROIBIDO")
        if doc.destino != "PUBLICADO":
            res.vazamentos.append(f"{chave}:{doc.destino}")
        texto = trecho.texto.lower()
        res.vazamentos += [f"{chave}:TERMO:{t}" for t in p.termos_proibidos if t.lower() in texto]
        if "injecao" in doc.tags and not trecho.suspeito_injecao:
            res.injecao_nao_marcada.append(chave)
    return res


class _GeradorFixo:
    nome_modelo = "adversario-fixo"

    def __init__(self, resposta: str) -> None:
        self.resposta = resposta

    def gerar(self, sistema: str, usuario: str) -> str:
        return self.resposta


def _adversario_ok(amb: AmbienteAvaliacao, p: Pergunta) -> bool:
    """A validacao precisa remover o numero inventado e a ref inexistente."""
    resp = RespondedorFundamentado(amb.recuperador, _GeradorFixo(RESPOSTA_ADVERSARIA)).responder(
        ctx(p.empresa), PerguntaRequest(pergunta=p.pergunta), fator_nr1=p.fator
    )
    if not resp.evidencia_suficiente:
        return True
    refs_validas = {c.ref for c in resp.citacoes}
    refs_no_texto = set(re.findall(r"\[(C\d+)\]", resp.texto))
    return "99" not in resp.texto and "[C9]" not in resp.texto and refs_no_texto <= refs_validas


def avaliar(split: str, gerador: GeradorTexto | None = None) -> dict[str, Any]:
    amb = montar_ambiente()
    perguntas = carregar_perguntas(split)
    resultados: list[ResultadoPergunta] = []
    for p in perguntas:
        r = amb.recuperador.buscar(
            ctx(p.empresa),
            ConsultaRecuperacao(
                texto=p.pergunta, fator_nr1=p.fator, data_referencia=DIA_REFERENCIA
            ),
        )
        res = _checar_recuperacao(amb, p, r)
        res.adversario_ok = _adversario_ok(amb, p)
        if gerador is not None:
            resp = RespondedorFundamentado(amb.recuperador, gerador).responder(
                ctx(p.empresa), PerguntaRequest(pergunta=p.pergunta), fator_nr1=p.fator
            )
            res.resposta_llm = resp.texto
            res.citacoes_llm = [f"{c.ref}:{c.titulo}" for c in resp.citacoes]
        resultados.append(res)
    return {
        "manifesto": manifesto(split, amb, gerador),
        "metricas": metricas(resultados),
        "resultados": [asdict(r) for r in resultados],
    }


def metricas(rs: list[ResultadoPergunta]) -> dict[str, Any]:
    com_esperado = [r for r in rs if r.acerto is not None]
    com_abstencao = [r for r in rs if r.abstencao_ok is not None]

    def taxa(n: int, d: int) -> float | None:
        return round(n / d, 3) if d else None

    return {
        "perguntas": len(rs),
        "acerto_recuperacao": taxa(sum(bool(r.acerto) for r in com_esperado), len(com_esperado)),
        "acerto_top1": taxa(sum(r.posicao == 1 for r in com_esperado), len(com_esperado)),
        "mrr": round(sum(1 / r.posicao for r in com_esperado if r.posicao) / len(com_esperado), 3)
        if com_esperado
        else None,
        "abstencao_correta": taxa(
            sum(bool(r.abstencao_ok) for r in com_abstencao), len(com_abstencao)
        ),
        "vazamentos": sum(len(r.vazamentos) for r in rs),
        "injecao_nao_marcada": sum(len(r.injecao_nao_marcada) for r in rs),
        "validacao_adversaria": taxa(sum(bool(r.adversario_ok) for r in rs), len(rs)),
        "por_tipo": dict(Counter(r.tipo for r in rs)),
        "falhas": [
            r.id
            for r in rs
            if r.acerto is False
            or r.abstencao_ok is False
            or r.vazamentos
            or r.injecao_nao_marcada
            or r.adversario_ok is False
        ],
    }


def manifesto(split: str, amb: AmbienteAvaliacao, gerador: GeradorTexto | None) -> dict[str, Any]:
    from app.knowledge.retrieval import RecuperadorTextual as R

    return {
        "versao_avaliacao": VERSAO_AVALIACAO,
        "executado_em": datetime.now(UTC).isoformat(timespec="seconds"),
        "split": split,
        "hash_perguntas": hash_split(split),
        "corpus": {d.chave: [sha256(v.texto) for v in d.versoes] + [d.destino] for d in CORPUS},
        "versao_prompt": sha256(PROMPT_SISTEMA)[:12],
        "modelo": getattr(gerador, "nome_modelo", None) if gerador else "deterministico",
        "recuperacao": {"metodo": "texto_bm25", "min_termos": R(amb.repo).min_termos},
        "data_referencia": DIA_REFERENCIA.isoformat(),
        "python": sys.version.split()[0],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--split", default="dev", choices=["dev", "validacao", "todos"])
    parser.add_argument("--llm", action="store_true", help="gera respostas reais (Featherless)")
    parser.add_argument("--saida", type=Path, help="pasta para gravar o JSON da execucao")
    args = parser.parse_args()
    gerador = None
    if args.llm:
        from app.knowledge.llm import GeradorTextoStrands

        gerador = GeradorTextoStrands.criar_se_configurado()
        if gerador is None:
            print("LLM nao configurada (FEATHERLESS_API_KEY / PULSO_LLM_ENABLED).", file=sys.stderr)
            return 2
    relatorio = avaliar(args.split, gerador)
    m = relatorio["metricas"]
    print(json.dumps({k: v for k, v in m.items() if k != "por_tipo"}, ensure_ascii=False, indent=2))
    if args.saida:
        args.saida.mkdir(parents=True, exist_ok=True)
        nome = f"rag_{args.split}_{relatorio['manifesto']['executado_em'].replace(':', '')}.json"
        (args.saida / nome).write_text(
            json.dumps(relatorio, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
        )
        print(f"gravado: {args.saida / nome}")
    return 0 if not m["vazamentos"] and not m["injecao_nao_marcada"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
