import React from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Shield, Cpu, MessageSquare, Database, FileText } from 'lucide-react';
import { Button } from '../components/ui/Button';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col justify-between overflow-x-hidden relative">
      {/* Background glowing blobs */}
      <div className="absolute top-1/4 left-1/4 h-96 w-96 -translate-x-1/2 rounded-full bg-indigo-600/10 blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 h-96 w-96 translate-x-1/2 rounded-full bg-violet-600/10 blur-[120px] pointer-events-none"></div>

      {/* Top Navbar */}
      <header className="container mx-auto px-6 h-20 flex items-center justify-between border-b border-slate-900 z-10">
        <div className="flex items-center gap-2">
          <BookOpen className="h-6 w-6 text-indigo-500" />
          <span className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
            KnowledgeHub AI
          </span>
        </div>
        <div className="flex items-center gap-4">
          <Link to="/login">
            <Button variant="ghost" size="sm">Sign In</Button>
          </Link>
          <Link to="/signup">
            <Button size="sm">Get Started</Button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center text-center px-6 py-20 z-10">
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/20 bg-indigo-500/5 text-xs text-indigo-400 font-semibold mb-4">
            <Shield className="h-3.5 w-3.5" /> Production Ready RAG Assistant
          </div>
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight bg-gradient-to-b from-white to-slate-400 bg-clip-text text-transparent leading-tight">
            Your Personal Knowledge space,<br />Supercharged by AI
          </h1>
          <p className="text-base sm:text-xl text-slate-400 max-w-2xl mx-auto font-normal leading-relaxed">
            Upload PDF, DOCX, manual notes, YouTube links, or code repositories.
            Ask questions, retrieve semantically, and get reliable citations.
            All indexed locally, answered securely.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Link to="/signup">
              <Button size="lg" className="w-full sm:w-auto">
                Create Free Account
              </Button>
            </Link>
            <Link to="/login">
              <Button variant="outline" size="lg" className="w-full sm:w-auto">
                Explore Demo Space
              </Button>
            </Link>
          </div>
        </div>

        {/* Feature Highlights Grid */}
        <section className="container mx-auto px-6 mt-32 max-w-6xl">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="rounded-xl border border-slate-900 bg-slate-950/20 p-6 text-left relative overflow-hidden group">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-4 group-hover:scale-110 transition-transform">
                <FileText className="h-5 w-5" />
              </div>
              <h3 className="text-lg font-bold text-slate-100 mb-2">Multi-Format Ingestion</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Seamless support for text files, PDF extraction via PyMuPDF, DOCX paragraphs,
                public GitHub repositories, and YouTube audio transcripts.
              </p>
            </div>

            <div className="rounded-xl border border-slate-900 bg-slate-950/20 p-6 text-left relative overflow-hidden group">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-4 group-hover:scale-110 transition-transform">
                <Cpu className="h-5 w-5" />
              </div>
              <h3 className="text-lg font-bold text-slate-100 mb-2">Local Vector Search</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Generates embeddings using BAAI/bge-small-en-v1.5 and processes vector similarity matching
                via Qdrant with sub-millisecond lookups.
              </p>
            </div>

            <div className="rounded-xl border border-slate-900 bg-slate-950/20 p-6 text-left relative overflow-hidden group">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-4 group-hover:scale-110 transition-transform">
                <MessageSquare className="h-5 w-5" />
              </div>
              <h3 className="text-lg font-bold text-slate-100 mb-2">Citations & Verification</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                No hallucinations. The AI assistant responds strictly within the boundaries of uploaded files
                and returns page-referenced citations.
              </p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="container mx-auto px-6 h-20 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 z-10 gap-2">
        <p>© 2026 KnowledgeHub AI. Built to meet elite enterprise interview standards.</p>
        <div className="flex gap-4">
          <a href="#" className="hover:text-indigo-400 transition-colors">Privacy Policy</a>
          <a href="#" className="hover:text-indigo-400 transition-colors">Terms of Service</a>
        </div>
      </footer>
    </div>
  );
};
