import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card } from '../components/ui/Card';
import { User, Shield, Mail, Calendar } from 'lucide-react';

export const ProfilePage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-8 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 sm:text-3xl">My Profile</h1>
        <p className="mt-1.5 text-sm text-slate-400">
          Manage your account credentials and system roles.
        </p>
      </div>

      <Card className="flex flex-col sm:flex-row items-center gap-6">
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-indigo-500/10 text-indigo-400 text-3xl font-bold border border-indigo-500/20">
          {user?.username?.[0]?.toUpperCase()}
        </div>
        <div className="space-y-1 text-center sm:text-left">
          <h2 className="text-xl font-bold text-slate-200">{user?.username}</h2>
          <div className="flex flex-wrap justify-center sm:justify-start gap-3 mt-1.5 text-sm text-slate-400">
            <span className="flex items-center gap-1"><Mail className="h-4 w-4" /> {user?.email}</span>
            <span className="flex items-center gap-1"><Shield className="h-4 w-4" /> Role: {user?.role}</span>
          </div>
        </div>
      </Card>
    </div>
  );
};
