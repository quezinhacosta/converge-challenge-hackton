import React from 'react';

export const metadata = {
  title: 'Pulso - Gestao de Riscos Psicossociais (NR-1) para o RH',
  description: 'Digital Worker de Gestao de Riscos Psicossociais (NR-1). Desafio Tako | Time Booleanas.',
};

/**
 * Layout raiz da aplicacao Pulso.
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased font-sans">
        {children}
      </body>
    </html>
  );
}
