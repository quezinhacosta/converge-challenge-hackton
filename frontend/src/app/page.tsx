import React from 'react';
import { AuditActionCenter } from '@/components/dp-dashboard/AuditActionCenter';
import { AbsenceManager } from '@/components/dp-dashboard/AbsenceManager';

/**
 * Main application dashboard landing page.
 */
export default function HomePage() {
  return (
    <main className="container mx-auto p-6 space-y-6">
      <header className="border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          PayTrust Governance Console
        </h1>
        <p className="text-sm text-slate-600">
          Powered by Tako - Converge Challenge Hackathon
        </p>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <AuditActionCenter
          pendingAnomalies={[]}
          onResolveAnomaly={async () => {}}
          totalBlockedAmount={0}
        />
        <AbsenceManager
          absences={[]}
          substitutions={[]}
          onDispatchInssNotice={async () => {}}
        />
      </section>
    </main>
  );
}
