import React from 'react';

export const metadata = {
  title: 'PayTrust - Governanca e Anti-Fraude na Folha de Pagamento',
  description: 'Digital Worker de Governanca, Anti-Fraude e Afastamentos. Powered by Tako.',
};

/**
 * Layout raiz da aplicacao frontend.
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased">
        {children}
      </body>
    </html>
  );
}
