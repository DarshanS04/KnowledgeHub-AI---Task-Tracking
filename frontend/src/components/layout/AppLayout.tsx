import React, { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  LayoutDashboard,
  MessageSquare,
  Upload,
  Search,
  User,
  Settings,
  LogOut,
  Shield,
  Menu,
  X,
  BookOpen,
} from 'lucide-react';
import { cn } from '../../utils/cn';

export const AppLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Chat Workspace', path: '/chat', icon: MessageSquare },
    { name: 'Upload Knowledge', path: '/upload', icon: Upload },
    { name: 'Semantic Search', path: '/search', icon: Search },
    { name: 'My Profile', path: '/profile', icon: User },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  // If user is admin, add admin dashboard link
  if (user?.role === 'admin') {
    navItems.push({ name: 'Admin Control', path: '/admin', icon: Shield });
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#090d16] text-slate-100">
      {/* Desktop Sidebar */}
      <aside className="hidden md:flex md:w-64 md:flex-col border-r border-slate-900 bg-[#0f172a]/40 backdrop-blur-md">
        <div className="flex h-16 items-center gap-2 px-6 border-b border-slate-900/50">
          <BookOpen className="h-6 w-6 text-indigo-500" />
          <span className="text-lg font-bold bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
            KnowledgeHub AI
          </span>
        </div>
        
        {/* Navigation links */}
        <nav className="flex-1 space-y-1.5 px-4 py-6 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 hover:bg-slate-800/60 hover:text-white',
                  isActive
                    ? 'bg-indigo-600/10 text-indigo-400 border border-indigo-500/20'
                    : 'text-slate-400'
                )
              }
            >
              <item.icon className="h-4 w-4" />
              {item.name}
            </NavLink>
          ))}
        </nav>

        {/* User profile segment in Sidebar bottom */}
        <div className="border-t border-slate-900/50 p-4">
          <div className="flex items-center gap-3 rounded-lg bg-slate-900/40 p-3 border border-slate-900">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-500/10 text-indigo-400 text-sm font-bold border border-indigo-500/20">
              {user?.username?.[0]?.toUpperCase() || 'U'}
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="truncate text-xs font-semibold text-slate-200">{user?.username}</p>
              <p className="truncate text-[10px] text-slate-400 capitalize">{user?.role}</p>
            </div>
            <button
              onClick={handleLogout}
              className="text-slate-400 hover:text-rose-400 transition-colors"
              title="Sign Out"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Mobile Header */}
        <header className="flex h-16 items-center justify-between border-b border-slate-900 px-6 md:hidden bg-[#0f172a]/30 backdrop-blur-md">
          <div className="flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-indigo-500" />
            <span className="text-base font-bold bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
              KnowledgeHub
            </span>
          </div>
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="rounded-lg p-1.5 hover:bg-slate-800 text-slate-300"
          >
            {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </header>

        {/* Mobile menu navigation */}
        {isMobileMenuOpen && (
          <div className="absolute inset-x-0 top-16 z-50 border-b border-slate-900 bg-[#0f172a] p-4 md:hidden shadow-2xl">
            <nav className="space-y-1">
              {navItems.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.path}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all',
                      isActive ? 'bg-indigo-600/15 text-indigo-400' : 'text-slate-400 hover:bg-slate-800/50'
                    )
                  }
                >
                  <item.icon className="h-4 w-4" />
                  {item.name}
                </NavLink>
              ))}
              <button
                onClick={handleLogout}
                className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-rose-400 hover:bg-rose-950/20"
              >
                <LogOut className="h-4 w-4" />
                Sign Out
              </button>
            </nav>
          </div>
        )}

        {/* Main Work Area */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-[#090d16]">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
