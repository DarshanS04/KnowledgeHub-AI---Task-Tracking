import React, { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Upload, Youtube, Github, StickyNote, CheckCircle, AlertTriangle } from 'lucide-react';
import { documentsApi } from '../api/documents';

export const UploadPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'files' | 'github' | 'youtube' | 'notes'>('files');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // File Upload State
  const [file, setFile] = useState<File | null>(null);

  // GitHub State
  const [githubUrl, setGithubUrl] = useState('');

  // YouTube State
  const [youtubeUrl, setYoutubeUrl] = useState('');

  // Notes State
  const [noteTitle, setNoteTitle] = useState('');
  const [noteContent, setNoteContent] = useState('');

  const clearMessages = () => {
    setSuccessMsg(null);
    setErrorMsg(null);
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    clearMessages();
    setIsSubmitting(true);
    try {
      await documentsApi.uploadFile(file);
      setSuccessMsg(`Successfully uploaded ${file.name}. Ingestion processing started in background.`);
      setFile(null);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.error?.message || 'Failed to upload file.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGithubClone = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!githubUrl) return;
    clearMessages();
    setIsSubmitting(true);
    try {
      await documentsApi.cloneGithub(githubUrl);
      setSuccessMsg('Repository clone dispatched successfully. Indexing started in background.');
      setGithubUrl('');
    } catch (err: any) {
      setErrorMsg(err.response?.data?.error?.message || 'Failed to clone repository.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleYoutubeFetch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!youtubeUrl) return;
    clearMessages();
    setIsSubmitting(true);
    try {
      await documentsApi.importYoutube(youtubeUrl);
      setSuccessMsg('YouTube transcript import dispatched. Ingesting text segments in background.');
      setYoutubeUrl('');
    } catch (err: any) {
      setErrorMsg(err.response?.data?.error?.message || 'Failed to import YouTube video.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNoteSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noteTitle || !noteContent) return;
    clearMessages();
    setIsSubmitting(true);
    try {
      await documentsApi.createNote(noteTitle, noteContent);
      setSuccessMsg(`Note "${noteTitle}" saved and vectorized successfully.`);
      setNoteTitle('');
      setNoteContent('');
    } catch (err: any) {
      setErrorMsg(err.response?.data?.error?.message || 'Failed to save manual note.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 sm:text-3xl">Ingest Knowledge</h1>
        <p className="mt-1.5 text-sm text-slate-400">
          Upload file assets or point the AI assistant to external repositories, note summaries, and transcripts.
        </p>
      </div>

      {successMsg && (
        <div className="flex items-center gap-2 rounded-lg border border-emerald-500/20 bg-emerald-500/10 p-4 text-xs text-emerald-400">
          <CheckCircle className="h-4 w-4 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {errorMsg && (
        <div className="flex items-center gap-2 rounded-lg border border-rose-500/20 bg-rose-500/10 p-4 text-xs text-rose-400">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 md:grid-cols-4">
        {/* Sidebar Selector */}
        <Card className="md:col-span-1 space-y-2 h-fit border-slate-900 bg-slate-950/20">
          <h3 className="text-xs font-bold uppercase text-slate-500 mb-4 tracking-wider">Select Source</h3>
          
          <button
            onClick={() => { setActiveTab('files'); clearMessages(); }}
            className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold text-left transition-colors ${
              activeTab === 'files'
                ? 'bg-indigo-600/10 border border-indigo-500/20 text-indigo-400'
                : 'text-slate-400 hover:bg-slate-800/40'
            }`}
          >
            <Upload className="h-4 w-4" />
            <span>Files (PDF, DOCX, TXT)</span>
          </button>

          <button
            onClick={() => { setActiveTab('github'); clearMessages(); }}
            className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold text-left transition-colors ${
              activeTab === 'github'
                ? 'bg-indigo-600/10 border border-indigo-500/20 text-indigo-400'
                : 'text-slate-400 hover:bg-slate-800/40'
            }`}
          >
            <Github className="h-4 w-4" />
            <span>GitHub Repository</span>
          </button>

          <button
            onClick={() => { setActiveTab('youtube'); clearMessages(); }}
            className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold text-left transition-colors ${
              activeTab === 'youtube'
                ? 'bg-indigo-600/10 border border-indigo-500/20 text-indigo-400'
                : 'text-slate-400 hover:bg-slate-800/40'
            }`}
          >
            <Youtube className="h-4 w-4" />
            <span>YouTube Transcript</span>
          </button>

          <button
            onClick={() => { setActiveTab('notes'); clearMessages(); }}
            className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold text-left transition-colors ${
              activeTab === 'notes'
                ? 'bg-indigo-600/10 border border-indigo-500/20 text-indigo-400'
                : 'text-slate-400 hover:bg-slate-800/40'
            }`}
          >
            <StickyNote className="h-4 w-4" />
            <span>Manual Notes</span>
          </button>
        </Card>

        {/* Tab Workspaces */}
        <Card className="md:col-span-3 border-slate-900">
          
          {/* Tab 1: File Upload */}
          {activeTab === 'files' && (
            <form onSubmit={handleFileUpload} className="space-y-6">
              <h2 className="text-lg font-bold text-slate-200">Upload Documents</h2>
              <div className="flex flex-col items-center justify-center p-12 border-2 border-dashed border-slate-800 rounded-xl bg-slate-900/10 hover:bg-slate-900/25 transition-colors cursor-pointer relative">
                <input
                  type="file"
                  accept=".pdf,.docx,.doc,.txt,.md"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  disabled={isSubmitting}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <div className="rounded-full bg-slate-950 border border-slate-800 p-4 mb-4">
                  <Upload className="h-6 w-6 text-indigo-400" />
                </div>
                <h3 className="text-sm font-bold text-slate-300">
                  {file ? file.name : 'Click or drag file to upload'}
                </h3>
                <p className="text-xs text-slate-500 mt-1">PDF, DOCX, TXT, or MD up to 50MB</p>
              </div>
              {file && (
                <div className="flex justify-end gap-3">
                  <Button type="button" variant="outline" onClick={() => setFile(null)}>Cancel</Button>
                  <Button type="submit" isLoading={isSubmitting}>Upload File</Button>
                </div>
              )}
            </form>
          )}

          {/* Tab 2: GitHub repository clone */}
          {activeTab === 'github' && (
            <form onSubmit={handleGithubClone} className="space-y-4">
              <h2 className="text-lg font-bold text-slate-200">Index Code Repository</h2>
              <p className="text-xs text-slate-400">
                Provide a public repository URL. The system will clone, scan code formats, and index semantic chunks.
              </p>
              <Input
                label="GitHub Repository URL"
                placeholder="e.g. https://github.com/username/project"
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
                disabled={isSubmitting}
              />
              <Button type="submit" className="w-full mt-2" isLoading={isSubmitting}>
                Clone & Index Repository
              </Button>
            </form>
          )}

          {/* Tab 3: YouTube import */}
          {activeTab === 'youtube' && (
            <form onSubmit={handleYoutubeFetch} className="space-y-4">
              <h2 className="text-lg font-bold text-slate-200">YouTube Transcript Ingest</h2>
              <p className="text-xs text-slate-400">
                Provide a YouTube video URL. We will download the transcripts, partition texts chronologically, and embed them.
              </p>
              <Input
                label="YouTube Video URL"
                placeholder="e.g. https://www.youtube.com/watch?v=VIDEO_ID"
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                disabled={isSubmitting}
              />
              <Button type="submit" className="w-full mt-2" isLoading={isSubmitting}>
                Fetch & Index Transcript
              </Button>
            </form>
          )}

          {/* Tab 4: Rich Notes */}
          {activeTab === 'notes' && (
            <form onSubmit={handleNoteSave} className="space-y-4">
              <h2 className="text-lg font-bold text-slate-200">Manual Note Ingestion</h2>
              <Input
                label="Note Title"
                placeholder="e.g. System Design Interview Guidelines"
                value={noteTitle}
                onChange={(e) => setNoteTitle(e.target.value)}
                disabled={isSubmitting}
              />
              <div className="w-full">
                <label className="mb-1.5 block text-xs font-medium text-slate-400">Note Content</label>
                <textarea
                  value={noteContent}
                  onChange={(e) => setNoteContent(e.target.value)}
                  disabled={isSubmitting}
                  placeholder="Write your study logs or summaries here..."
                  className="flex min-h-[250px] w-full rounded-lg border border-slate-800 bg-slate-900/50 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>
              <Button type="submit" className="w-full" isLoading={isSubmitting}>
                Save & Index Note
              </Button>
            </form>
          )}

        </Card>
      </div>
    </div>
  );
};
export default UploadPage;
