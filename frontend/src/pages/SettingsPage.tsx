import React from 'react';
import { Card } from '../components/ui/Card';
import { ToggleLeft, Moon, Bell, ShieldAlert } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  return (
    <div className="space-y-8 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 sm:text-3xl">Settings</h1>
        <p className="mt-1.5 text-sm text-slate-400">
          Customize UI theme, notification systems, and security.
        </p>
      </div>

      <Card className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Moon className="h-5 w-5 text-indigo-400" />
            <div>
              <p className="text-sm font-semibold text-slate-200">Force Dark Mode</p>
              <p className="text-xs text-slate-500">Enable premium theme aesthetics by default</p>
            </div>
          </div>
          <div className="h-6 w-11 rounded-full bg-indigo-600 p-0.5 cursor-pointer">
            <div className="h-5 w-5 translate-x-5 rounded-full bg-white transition-transform"></div>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Bell className="h-5 w-5 text-indigo-400" />
            <div>
              <p className="text-sm font-semibold text-slate-200">Processing Email Notifications</p>
              <p className="text-xs text-slate-500">Get notified when long jobs finish</p>
            </div>
          </div>
          <div className="h-6 w-11 rounded-full bg-slate-800 p-0.5 cursor-pointer">
            <div className="h-5 w-5 rounded-full bg-slate-400 transition-transform"></div>
          </div>
        </div>
      </Card>
    </div>
  );
};
