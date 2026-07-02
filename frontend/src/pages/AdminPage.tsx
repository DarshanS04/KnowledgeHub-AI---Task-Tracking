import React from 'react';
import { Card } from '../components/ui/Card';
import { ShieldAlert, Users, FolderKanban, Terminal } from 'lucide-react';

export const AdminPage: React.FC = () => {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 sm:text-3xl">Admin Control Center</h1>
        <p className="mt-1.5 text-sm text-slate-400">
          Supervise user registrations, vector storage consumption, and pipeline errors.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <Card className="flex items-center gap-4">
          <div className="rounded-lg bg-indigo-500/10 p-3 text-indigo-400 border border-indigo-500/20">
            <Users className="h-6 w-6" />
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wider">Total Registrations</p>
            <p className="text-2xl font-extrabold text-slate-200 mt-1">42 Users</p>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="rounded-lg bg-indigo-500/10 p-3 text-indigo-400 border border-indigo-500/20">
            <FolderKanban className="h-6 w-6" />
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wider">Active Pipelines</p>
            <p className="text-2xl font-extrabold text-slate-200 mt-1">3 Running</p>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="rounded-lg bg-indigo-500/10 p-3 text-indigo-400 border border-indigo-500/20">
            <ShieldAlert className="h-6 w-6" />
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wider">System Errors</p>
            <p className="text-2xl font-extrabold text-slate-200 mt-1">0 Flagged</p>
          </div>
        </Card>
      </div>
    </div>
  );
};
