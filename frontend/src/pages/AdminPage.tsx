import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import {
  Users,
  FolderKanban,
  ShieldAlert,
  Clock,
  Trash2,
  RefreshCcw,
  AlertOctagon,
  FileText,
  UserCheck,
} from 'lucide-react';
import { adminApi } from '../api/admin';
import { SystemStatsResponse, UserResponse } from '../types';

export const AdminPage: React.FC = () => {
  const [stats, setStats] = useState<SystemStatsResponse | null>(null);
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [uploadLogs, setUploadLogs] = useState<any[]>([]);
  const [queueJobs, setQueueJobs] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'users' | 'logs' | 'queue'>('users');
  const [isLoading, setIsLoading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchStatsAndTabs = async () => {
    setIsLoading(true);
    try {
      const statsData = await adminApi.getStats();
      setStats(statsData);
      
      if (activeTab === 'users') {
        const usersData = await adminApi.listUsers();
        setUsers(usersData);
      } else if (activeTab === 'logs') {
        const logsData = await adminApi.listUploadLogs();
        setUploadLogs(logsData);
      } else if (activeTab === 'queue') {
        const queueData = await adminApi.listProcessingQueue();
        setQueueJobs(queueData);
      }
    } catch (e) {
      console.error('Failed to load admin telemetry:', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStatsAndTabs();
  }, [activeTab]);

  const handleDeleteUser = async (id: string) => {
    if (!window.confirm('Delete this user? All their conversations, uploaded documents, and vector storage points will be permanently cascaded and deleted.')) {
      return;
    }
    setDeletingId(id);
    try {
      await adminApi.deleteUser(id);
      setUsers((prev) => prev.filter((u) => u.id !== id));
      // Refresh counts
      const updatedStats = await adminApi.getStats();
      setStats(updatedStats);
    } catch (e) {
      console.error(e);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 sm:text-3xl">Admin Control Center</h1>
          <p className="mt-1.5 text-sm text-slate-400">
            System administration telemetry, user registries, audit logs, and asynchronous pipelines.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchStatsAndTabs} className="gap-2">
          <RefreshCcw className="h-4 w-4" /> Sync Stats
        </Button>
      </div>

      {/* Aggregate Counters Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-5">
        <Card className="border-slate-900 bg-slate-950/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Registrations</p>
              <p className="text-2xl font-extrabold text-slate-200 mt-1">{stats?.total_users ?? 0}</p>
            </div>
            <Users className="h-5 w-5 text-indigo-400" />
          </div>
        </Card>
        <Card className="border-slate-900 bg-slate-950/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Documents Ingested</p>
              <p className="text-2xl font-extrabold text-slate-200 mt-1">{stats?.total_documents ?? 0}</p>
            </div>
            <FileText className="h-5 w-5 text-indigo-400" />
          </div>
        </Card>
        <Card className="border-slate-900 bg-slate-950/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Indexed Chunks</p>
              <p className="text-2xl font-extrabold text-slate-200 mt-1">{stats?.total_chunks ?? 0}</p>
            </div>
            <FolderKanban className="h-5 w-5 text-indigo-400" />
          </div>
        </Card>
        <Card className="border-slate-900 bg-slate-950/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Conversations</p>
              <p className="text-2xl font-extrabold text-slate-200 mt-1">{stats?.total_conversations ?? 0}</p>
            </div>
            <Clock className="h-5 w-5 text-indigo-400" />
          </div>
        </Card>
        <Card className="border-slate-900 bg-slate-950/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Inference Queries</p>
              <p className="text-2xl font-extrabold text-slate-200 mt-1">{stats?.total_messages ?? 0}</p>
            </div>
            <ShieldAlert className="h-5 w-5 text-indigo-400" />
          </div>
        </Card>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-900">
        <div className="flex gap-4">
          {[
            { id: 'users', label: 'Registered Users', icon: Users },
            { id: 'logs', label: 'Ingestion Audit Logs', icon: FileText },
            { id: 'queue', label: 'Active Pipeline Queue', icon: Clock },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 border-b-2 px-1 pb-4 text-sm font-semibold transition-colors ${
                activeTab === tab.id
                  ? 'border-indigo-500 text-indigo-400'
                  : 'border-transparent text-slate-400 hover:text-slate-300'
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Workspace Display Area */}
      <Card className="border-slate-900">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center p-12 text-slate-500">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent mb-3"></div>
            <p className="text-sm">Loading details...</p>
          </div>
        ) : (
          <>
            {/* Tab 1: User Registry */}
            {activeTab === 'users' && (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-350">
                  <thead className="border-b border-slate-800 text-xs uppercase text-slate-500 font-bold">
                    <tr>
                      <th className="py-4 px-3">Username</th>
                      <th className="py-4 px-3">Email Address</th>
                      <th className="py-4 px-3">Role</th>
                      <th className="py-4 px-3">State</th>
                      <th className="py-4 px-3">Registered At</th>
                      <th className="py-4 px-3 text-right">Delete</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-900">
                    {users.map((u) => (
                      <tr key={u.id} className="hover:bg-slate-900/10">
                        <td className="py-4 px-3 font-semibold text-slate-200">{u.username}</td>
                        <td className="py-4 px-3 text-slate-400">{u.email}</td>
                        <td className="py-4 px-3 text-slate-400 uppercase text-[10px] font-bold">{u.role}</td>
                        <td className="py-4 px-3">
                          <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold ${
                            u.is_active
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                              : 'bg-slate-800 text-slate-500'
                          }`}>
                            {u.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="py-4 px-3 text-slate-400">
                          {new Date(u.created_at).toLocaleDateString()}
                        </td>
                        <td className="py-4 px-3 text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            disabled={deletingId === u.id || u.role === 'admin'}
                            onClick={() => handleDeleteUser(u.id)}
                            className="text-rose-500 hover:bg-rose-950/20 disabled:opacity-40"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Tab 2: Ingestion logs */}
            {activeTab === 'logs' && (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-350">
                  <thead className="border-b border-slate-800 text-xs uppercase text-slate-500 font-bold">
                    <tr>
                      <th className="py-4 px-3">Action</th>
                      <th className="py-4 px-3">User ID</th>
                      <th className="py-4 px-3">Doc ID</th>
                      <th className="py-4 px-3">IP Address</th>
                      <th className="py-4 px-3">Status</th>
                      <th className="py-4 px-3">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-900">
                    {uploadLogs.length > 0 ? (
                      uploadLogs.map((log) => (
                        <tr key={log.id} className="hover:bg-slate-900/10">
                          <td className="py-4 px-3 font-semibold text-slate-200 uppercase text-[10px]">
                            {log.action}
                          </td>
                          <td className="py-4 px-3 text-slate-500 font-mono text-xs">{log.user_id}</td>
                          <td className="py-4 px-3 text-slate-500 font-mono text-xs">{log.document_id || 'None'}</td>
                          <td className="py-4 px-3 text-slate-400">{log.ip_address || '127.0.0.1'}</td>
                          <td className="py-4 px-3">
                            <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                              log.status === 'success'
                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                            }`}>
                              {log.status}
                            </span>
                          </td>
                          <td className="py-4 px-3 text-slate-400">
                            {new Date(log.created_at).toLocaleString()}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={6} className="text-center py-8 text-slate-500">
                          No ingestion activity logged.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {/* Tab 3: Active queue */}
            {activeTab === 'queue' && (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-350">
                  <thead className="border-b border-slate-800 text-xs uppercase text-slate-500 font-bold">
                    <tr>
                      <th className="py-4 px-3">Document ID</th>
                      <th className="py-4 px-3">Pipeline Step</th>
                      <th className="py-4 px-3">Progress</th>
                      <th className="py-4 px-3">Status</th>
                      <th className="py-4 px-3">Created At</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-900">
                    {queueJobs.length > 0 ? (
                      queueJobs.map((job) => (
                        <tr key={job.id} className="hover:bg-slate-900/10">
                          <td className="py-4 px-3 text-slate-400 font-mono text-xs">{job.document_id}</td>
                          <td className="py-4 px-3 capitalize text-slate-200">{job.job_type}</td>
                          <td className="py-4 px-3">
                            <div className="flex items-center gap-2">
                              <div className="w-24 bg-slate-900 border border-slate-800 rounded-full h-2 overflow-hidden">
                                <div
                                  className="bg-indigo-500 h-full transition-all duration-300"
                                  style={{ width: `${job.progress}%` }}
                                ></div>
                              </div>
                              <span className="text-xs text-slate-400 font-bold">{job.progress}%</span>
                            </div>
                          </td>
                          <td className="py-4 px-3">
                            <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold ${
                              job.status === 'completed'
                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                : job.status === 'failed'
                                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                                : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 animate-pulse'
                            }`}>
                              {job.status}
                            </span>
                          </td>
                          <td className="py-4 px-3 text-slate-400">
                            {new Date(job.created_at).toLocaleString()}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={5} className="text-center py-8 text-slate-500">
                          No pipeline jobs in history.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </Card>
    </div>
  );
};
export default AdminPage;
