import React from 'react';
import { Card } from '../components/ui/Card';
import { Upload, Youtube, Github, StickyNote, HelpCircle } from 'lucide-react';
import { Button } from '../components/ui/Button';

export const UploadPage: React.FC = () => {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 sm:text-3xl">Upload Knowledge</h1>
        <p className="mt-1.5 text-sm text-slate-400">
          Feed files, URLs, or notes into your local vector space database.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-4">
        {/* Upload Sources Selectors */}
        <Card className="md:col-span-1 space-y-2 h-fit">
          <h3 className="text-xs font-bold uppercase text-slate-500 mb-4 tracking-wider">Select Source</h3>
          <button className="flex w-full items-center gap-3 rounded-lg bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 px-3 py-2.5 text-sm font-semibold text-left">
            <Upload className="h-4 w-4" />
            <span>Files (PDF, DOCX, TXT)</span>
          </button>
          <button className="flex w-full items-center gap-3 rounded-lg text-slate-400 hover:bg-slate-800/40 px-3 py-2.5 text-sm font-medium text-left">
            <Github className="h-4 w-4" />
            <span>GitHub Repository</span>
          </button>
          <button className="flex w-full items-center gap-3 rounded-lg text-slate-400 hover:bg-slate-800/40 px-3 py-2.5 text-sm font-medium text-left">
            <Youtube className="h-4 w-4" />
            <span>YouTube Transcript</span>
          </button>
          <button className="flex w-full items-center gap-3 rounded-lg text-slate-400 hover:bg-slate-800/40 px-3 py-2.5 text-sm font-medium text-left">
            <StickyNote className="h-4 w-4" />
            <span>Manual Notes</span>
          </button>
        </Card>

        {/* Workspace Drag-and-Drop Area */}
        <Card className="md:col-span-3 flex flex-col items-center justify-center p-12 min-h-[400px] border-dashed border-2 border-slate-800/60 bg-slate-900/10">
          <div className="rounded-full bg-slate-900 border border-slate-800 p-4 mb-4">
            <Upload className="h-8 w-8 text-indigo-400" />
          </div>
          <h3 className="text-base font-bold text-slate-200 mb-1">Drag and drop your files here</h3>
          <p className="text-xs text-slate-500 mb-6">PDF, DOCX, TXT, or MD up to 50MB</p>
          <Button>Browse Files</Button>
        </Card>
      </div>
    </div>
  );
};
