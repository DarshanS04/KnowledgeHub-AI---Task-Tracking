import React from 'react';
import { Card } from '../components/ui/Card';
import { FileText, Trash2, Calendar, Database } from 'lucide-react';
import { Button } from '../components/ui/Button';

export const DocumentsPage: React.FC = () => {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 sm:text-3xl">My Documents</h1>
          <p className="mt-1.5 text-sm text-slate-400">
            View, filter, or remove ingested documents in your knowledge space.
          </p>
        </div>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="border-b border-slate-800 text-xs uppercase text-slate-500 font-bold">
              <tr>
                <th className="py-4 px-3">Name</th>
                <th className="py-4 px-3">Type</th>
                <th className="py-4 px-3">Chunks</th>
                <th className="py-4 px-3">Ingested At</th>
                <th className="py-4 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-900">
              <tr className="hover:bg-slate-900/10">
                <td className="py-4 px-3 font-semibold text-slate-200">AWS_Solutions_Architect.pdf</td>
                <td className="py-4 px-3 text-slate-400">PDF</td>
                <td className="py-4 px-3">12</td>
                <td className="py-4 px-3">Jul 1, 2026</td>
                <td className="py-4 px-3 text-right">
                  <Button variant="ghost" size="sm" className="text-rose-500 hover:bg-rose-950/20">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
