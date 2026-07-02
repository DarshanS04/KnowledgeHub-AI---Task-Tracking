import React, { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Moon, Bell, Shield, Database, Trash2 } from 'lucide-react';
import { Button } from '../components/ui/Button';

export const SettingsPage: React.FC = () => {
  const [darkMode, setDarkMode] = useState(true);
  const [notifications, setNotifications] = useState(false);
  const [autoIndex, setAutoIndex] = useState(true);

  return (
    <div className="space-y-8 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 sm:text-3xl">Settings</h1>
        <p className="mt-1.5 text-sm text-slate-400">
          Configure preference modules, document storage limits, and system parameters.
        </p>
      </div>

      <Card className="space-y-6 border-slate-900">
        {/* Toggle Dark Mode */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Moon className="h-5 w-5 text-indigo-400" />
            <div>
              <p className="text-sm font-semibold text-slate-200">Force Dark Mode</p>
              <p className="text-xs text-slate-500">Enables premium aesthetic styling across panels (always dark by default)</p>
            </div>
          </div>
          <button
            onClick={() => setDarkMode(!darkMode)}
            className={`h-6 w-11 rounded-full p-0.5 transition-colors cursor-pointer ${
              darkMode ? 'bg-indigo-650' : 'bg-slate-800'
            }`}
          >
            <div className={`h-5 w-5 rounded-full bg-white transition-transform ${
              darkMode ? 'translate-x-5' : 'translate-x-0'
            }`}></div>
          </button>
        </div>

        {/* Toggle Notifications */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Bell className="h-5 w-5 text-indigo-400" />
            <div>
              <p className="text-sm font-semibold text-slate-200">Processing Email Alerts</p>
              <p className="text-xs text-slate-500">Receive notifications when long-running GitHub repo clones complete indexing</p>
            </div>
          </div>
          <button
            onClick={() => setNotifications(!notifications)}
            className={`h-6 w-11 rounded-full p-0.5 transition-colors cursor-pointer ${
              notifications ? 'bg-indigo-650' : 'bg-slate-800'
            }`}
          >
            <div className={`h-5 w-5 rounded-full bg-white transition-transform ${
              notifications ? 'translate-x-5' : 'translate-x-0'
            }`}></div>
          </button>
        </div>

        {/* Toggle Auto Vector Ingestion */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Database className="h-5 w-5 text-indigo-400" />
            <div>
              <p className="text-sm font-semibold text-slate-200">Auto-Index Uploads</p>
              <p className="text-xs text-slate-500">Instantly trigger embedding pipelines for newly uploaded files</p>
            </div>
          </div>
          <button
            onClick={() => setAutoIndex(!autoIndex)}
            className={`h-6 w-11 rounded-full p-0.5 transition-colors cursor-pointer ${
              autoIndex ? 'bg-indigo-650' : 'bg-slate-800'
            }`}
          >
            <div className={`h-5 w-5 rounded-full bg-white transition-transform ${
              autoIndex ? 'translate-x-5' : 'translate-x-0'
            }`}></div>
          </button>
        </div>
      </Card>

      {/* Danger Zone */}
      <Card className="border-rose-950/20 bg-rose-950/5 space-y-4">
        <h3 className="text-base font-bold text-rose-400 flex items-center gap-2">
          <Shield className="h-5 w-5" /> Danger Zone
        </h3>
        <p className="text-xs text-slate-400">
          Deleting your account is permanent. This will cascade delete all uploads, custom notes, Qdrant vectors, and conversation histories.
        </p>
        <Button variant="danger" className="gap-2">
          <Trash2 className="h-4 w-4" /> Delete Account
        </Button>
      </Card>
    </div>
  );
};
export default SettingsPage;
