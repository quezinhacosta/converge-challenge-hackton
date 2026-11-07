import React from 'react';

export const metadata = {
  title: 'PayTrust - Payroll Governance & Anti-Fraud',
  description: 'Digital Worker for Payroll Governance, Anti-Fraud, and Leaves. Powered by Tako.',
};

/**
 * Root application layout.
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
