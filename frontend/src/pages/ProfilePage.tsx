import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { User, Shield, Mail, Calendar, CheckCircle, AlertTriangle } from 'lucide-react';

export const ProfilePage: React.FC = () => {
  const { user } = useAuth();
  
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccess(null);
    setError(null);

    if (!oldPassword || !newPassword || !confirmPassword) {
      setError('Please fill in all password fields.');
      return;
    }

    if (newPassword.length < 8) {
      setError('New password must be at least 8 characters long.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('New passwords do not match.');
      return;
    }

    setIsSubmitting(true);
    try {
      // In the next phase, we'll connect this to a PUT /users/password endpoint.
      // For now, we simulate success with a delay.
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setSuccess('Password updated successfully.');
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      setError('Failed to update password.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-8 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 sm:text-3xl">My Profile</h1>
        <p className="mt-1.5 text-sm text-slate-400">
          Manage your personal details and account credentials.
        </p>
      </div>

      {/* User Information Panel */}
      <Card className="flex flex-col sm:flex-row items-center gap-6 border-slate-900 bg-slate-950/20">
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-indigo-500/10 text-indigo-400 text-3xl font-bold border border-indigo-500/20">
          {user?.username?.[0]?.toUpperCase()}
        </div>
        <div className="space-y-1.5 text-center sm:text-left">
          <h2 className="text-xl font-bold text-slate-200">{user?.username}</h2>
          <div className="flex flex-wrap justify-center sm:justify-start gap-4 text-xs text-slate-400">
            <span className="flex items-center gap-1.5"><Mail className="h-4 w-4 text-indigo-400" /> {user?.email}</span>
            <span className="flex items-center gap-1.5"><Shield className="h-4 w-4 text-indigo-400" /> Role: <span className="capitalize">{user?.role}</span></span>
            <span className="flex items-center gap-1.5"><Calendar className="h-4 w-4 text-indigo-400" /> Member since: {new Date(user?.created_at || '').toLocaleDateString()}</span>
          </div>
        </div>
      </Card>

      {/* Password Reset Section */}
      <Card className="border-slate-900">
        <h3 className="text-base font-bold text-slate-200 mb-4">Change Password</h3>
        
        <form onSubmit={handlePasswordChange} className="space-y-4 max-w-md">
          {success && (
            <div className="flex items-center gap-2 rounded-lg border border-emerald-500/20 bg-emerald-500/10 p-3 text-xs text-emerald-400">
              <CheckCircle className="h-4 w-4 shrink-0" />
              <span>{success}</span>
            </div>
          )}

          {error && (
            <div className="flex items-center gap-2 rounded-lg border border-rose-500/20 bg-rose-500/10 p-3 text-xs text-rose-400">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <Input
            type="password"
            label="Current Password"
            placeholder="••••••••"
            value={oldPassword}
            onChange={(e) => setOldPassword(e.target.value)}
            disabled={isSubmitting}
          />

          <Input
            type="password"
            label="New Password"
            placeholder="Min. 8 characters"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            disabled={isSubmitting}
          />

          <Input
            type="password"
            label="Confirm New Password"
            placeholder="Repeat new password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            disabled={isSubmitting}
          />

          <Button type="submit" isLoading={isSubmitting}>Update Password</Button>
        </form>
      </Card>
    </div>
  );
};
export default ProfilePage;
