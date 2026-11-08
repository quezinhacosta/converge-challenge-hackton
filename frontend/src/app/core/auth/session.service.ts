import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import type { SupabaseClient, Session } from '@supabase/supabase-js';
import { environment } from '../../../environments/environment';
export interface Company {id:string;nome:string;papeis:string[];}
@Injectable({providedIn:'root'})
export class SessionService {
 private http=inject(HttpClient);
 private clientPromise:Promise<SupabaseClient>|null=null;
 private restorePromise:Promise<void>|null=null;
 private accessToken:string|null=null; private companyId:string|null=null; private userId:string|null=null;
 private generation=0;
 readonly demo=signal(false); readonly userEmail=signal(''); readonly companies=signal<Company[]>([]); readonly company=signal<Company|null>(null);
 readonly authenticated=signal(false); readonly ready=signal(false); readonly error=signal('');
 private async client():Promise<SupabaseClient> {
  if(!this.clientPromise)this.clientPromise=firstValueFrom(this.http.get<{url:string;publishableKey:string}>(environment.apiUrl+'/auth/config')).then(async config=>{
   const {createClient}=await import('@supabase/supabase-js');
   const client=createClient(config.url,config.publishableKey,{auth:{persistSession:true,autoRefreshToken:true,detectSessionInUrl:false,storageKey:'vytai.auth'}});
   client.auth.onAuthStateChange((_event,session)=>{
    if(!session){this.clear();return;}
    if(this.userId!==session.user.id){this.generation++;this.companyId=null;this.company.set(null);this.companies.set([]);this.authenticated.set(false);}
    this.userId=session.user.id;this.accessToken=session.access_token;this.userEmail.set(session.user.email||'');
    // Nenhuma chamada Supabase dentro do callback de auth.
   });return client;
  }).catch(error=>{this.clientPromise=null;throw error;});
  return this.clientPromise;
 }
 restore():Promise<void> {
  if(!this.restorePromise)this.restorePromise=this.restoreSession();
  return this.restorePromise;
 }
 private async restoreSession():Promise<void>{
  try{
   try{const context=await firstValueFrom(this.http.get<{empresa:Company;demo:boolean}>(environment.apiUrl+'/auth/context'));if(context.demo){this.demo.set(true);this.companies.set([context.empresa]);this.selectCompany(context.empresa.id);return;}}catch{/* Producao sem token continua no login Supabase. */}
   const {data,error}=await (await this.client()).auth.getSession();if(error)throw error;if(data.session)await this.accept(data.session);}
  catch{this.error.set('Login indisponível. Confira a configuração do servidor.');}
  finally{this.ready.set(true);}
 }
 async signIn(email:string,password:string):Promise<void>{
  this.error.set('');const {data,error}=await (await this.client()).auth.signInWithPassword({email:email.trim(),password});
  if(error||!data.session)throw new Error('Não foi possível entrar. Confira email e senha.');
  await this.accept(data.session);
 }
 private async accept(session:Session):Promise<void>{
  this.accessToken=session.access_token;this.userId=session.user.id;this.userEmail.set(session.user.email||'');const epoch=++this.generation;
  const companies=await firstValueFrom(this.http.get<Company[]>(environment.apiUrl+'/auth/empresas'));
  if(epoch!==this.generation)return;
  this.companies.set(companies);
  const selected=companies.find(c=>c.id===this.companyId)||(companies.length===1?companies[0]:null);
  if(selected)this.selectCompany(selected.id);
  else {this.companyId=null;this.company.set(null);this.authenticated.set(false);}
  if(!companies.length)this.error.set('Sua conta entrou, mas ainda não tem vínculo ativo com o RH de uma empresa. Solicite o acesso ao administrador.');
 }
 selectCompany(id:string):void {const selected=this.companies().find(c=>c.id===id);if(!selected)throw new Error('Empresa não autorizada.');this.companyId=id;this.company.set(selected);this.authenticated.set(true);}
 // Compatibilidade com adaptadores existentes; o backend sempre verifica token e vinculo.
 setSession(token:string,empresaId:string):void {this.accessToken=token;this.companyId=empresaId;}
 clear():void {this.generation++;this.demo.set(false);this.accessToken=null;this.companyId=null;this.userId=null;this.company.set(null);this.companies.set([]);this.userEmail.set('');this.authenticated.set(false);}
 async signOut():Promise<void>{try{if(this.clientPromise)await (await this.clientPromise).auth.signOut({scope:'local'});}finally{this.clear();}}
 headers():Record<string,string>{return this.accessToken?{Authorization:`Bearer ${this.accessToken}`,...(this.companyId?{'X-Empresa-Id':this.companyId}:{})}:{};}
}
