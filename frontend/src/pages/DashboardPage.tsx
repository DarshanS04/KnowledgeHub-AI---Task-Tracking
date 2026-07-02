import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card } from '../components/ui/Card';
import {
  FileText,
  MessageSquare,
  HardDrive,
  Database,
  Clock,
  ArrowRight,
  TrendingUp,
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();

  // Mock stats for Phase 1
  const stats = [
    { name: 'Total Documents', value: '12', icon: FileText, change: '+2 this week', changeType: 'positive' },
    { name: 'Questions Asked', value: '148', icon: MessageSquare, change: '+24 today', changeType: 'positive' },
    { name: 'Vector Chunks', value: '1,420', icon: Database, change: '+184 recently', changeType: 'positive' },
    { name: 'Index Storage Used', value: '18.4 MB', icon: HardDrive, change: 'of 50 GB limit', changeType: 'neutral' },
  ];

  const recentUploads = [
    { id: '1', filename: 'AWS_Solutions_Architect.pdf', size: '4.2 MB', type: 'PDF', date: '2 hours ago', status: 'completed' },
    { id: '2', filename: 'knowledgehub-architecture.md', size: '12 KB', type: 'Markdown', date: 'Yesterday', status: 'completed' },
    { id: '3', filename: 'youtube-python-rag-course.json', size: '85 KB', type: 'YouTube', date: '3 days ago', status: 'completed' },
  ];

  const recentChats = [
    { id: '1', title: 'Deep dive into LangChain splitters', date: '5 mins ago' },
    { id: '2', title: 'How does Qdrant index metadata payload?', date: '1 hour ago' },
    { id: '3', title: 'Debugging SQLAlchemy asyncpg session lifecycle', date: 'Yesterday' },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome banner */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100 sm:text-3xl">
          Welcome back, {user?.username}!
        </h1>
        <p className="mt-1.5 text-sm text-slate-400">
          Here is a summary of your local knowledge space and latest queries.
        </p>
      </div>

      {/* Grid containing stats cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.name} className="relative overflow-hidden group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{stat.name}</p>
                <p className="mt-2 text-3xl font-bold text-slate-100">{stat.value}</p>
              </div>
              <div className="rounded-lg bg-indigo-500/10 p-3 text-indigo-400 border border-indigo-500/20 group-hover:scale-105 transition-transform duration-300">
                <stat.icon className="h-6 w-6" />
              </div>
            </div>
            <div className="mt-4 flex items-center gap-1.5 text-xs">
              <span
                className={
                  stat.changeType === 'positive'
                    ? 'text-emerald-400 font-semibold'
                    : 'text-slate-400'
                }
              >
                {stat.change}
              </span>
            </div>
          </Card>
        ))}
      </div>

      {/* Grid of recent activities */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        {/* Recent Ingested Documents */}
        <Card className="flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold text-slate-100">Recent Uploads</h2>
            <Link to="/upload" className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors">
              Ingest More <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
          <div className="flex-1 space-y-4">
            {recentUploads.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between rounded-lg bg-slate-900/30 p-3 border border-slate-900/60"
              >
                <div className="flex items-center gap-3 overflow-hidden">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-500/5 text-indigo-400 border border-indigo-500/10 text-xs font-bold uppercase">
                    {doc.type.slice(0, 3)}
                  </div>
                  <div className="overflow-hidden">
                    <p className="truncate text-sm font-medium text-slate-200">{doc.filename}</p>
                    <p className="text-xs text-slate-400">{doc.size} • {doc.date}</p>
                  </div>
                </div>
                <div className="inline-flex items-center rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-medium text-emerald-400 border border-emerald-500/20">
                  Ready
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Recent Conversations */}
        <Card className="flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold text-slate-100">Recent Conversations</h2>
            <Link to="/chat" className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors">
              Open Chat <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
          <div className="flex-1 space-y-4">
            {recentChats.map((chat) => (
              <div
                key={chat.id}
                className="flex items-center justify-between rounded-lg bg-slate-900/30 p-3 border border-slate-900/60 hover:bg-slate-900/50 transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-3 overflow-hidden">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-500/5 text-indigo-400 border border-indigo-500/10">
                    <MessageSquare className="h-4 w-4" />
                  </div>
                  <div className="overflow-hidden">
                    <p className="truncate text-sm font-medium text-slate-200">{chat.title}</p>
                    <p className="text-xs text-slate-400">{chat.date}</p>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-slate-500 shrink-0" />
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Analytics Mini Panel */}
      <Card className="bg-slate-900/30 border-slate-900">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="h-5 w-5 text-indigo-400" />
          <h2 className="text-base font-bold text-slate-200">System Inference Performance</h2>
        </div>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-3 text-center">
          <div className="p-4 rounded-lg bg-slate-900/20 border border-slate-900">
            <p className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Avg. Response Time</p>
            <p className="text-2xl font-extrabold text-indigo-400 mt-1">1.84s</p>
          </div>
          <div className="p-4 rounded-lg bg-slate-900/20 border border-slate-900">
            <p className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Retrieval Accuracy (mAP)</p>
            <p className="text-2xl font-extrabold text-indigo-400 mt-1">94.8%</p>
          </div>
          <div className="p-4 rounded-lg bg-slate-900/20 border border-slate-900">
            <p className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Embedding Cache Hits</p>
            <p className="text-2xl font-extrabold text-indigo-400 mt-1">88.5%</p>
          </div>
        </div>
      </Card>
    </div>
  );
};
