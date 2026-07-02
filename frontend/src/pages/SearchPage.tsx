import React, { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Search, SlidersHorizontal, AlertTriangle, FileText, Database } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { searchApi } from '../api/search';
import { SearchResult } from '../types';

export const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [sourceType, setSourceType] = useState<string>('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setSearched(true);
    try {
      const hits = await searchApi.executeSearch(query, sourceType || undefined, 5);
      setResults(hits);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 sm:text-3xl">Semantic Search</h1>
        <p className="mt-1.5 text-sm text-slate-400">
          Query your vector database collection directly and view exact chunk similarity metrics.
        </p>
      </div>

      {/* Query Bar */}
      <form onSubmit={handleSearch} className="space-y-4">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search keyword contexts, questions, or conceptual definitions..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-900/40 py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none"
            />
          </div>
          <Button type="submit" disabled={isLoading || !query.trim()}>
            {isLoading ? 'Searching...' : 'Search'}
          </Button>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4 bg-slate-950/20 p-3 rounded-lg border border-slate-900 text-xs text-slate-400">
          <div className="flex items-center gap-1.5 font-bold"><SlidersHorizontal className="h-3.5 w-3.5 text-indigo-400" /> Filter by Source:</div>
          <div className="flex gap-2">
            {[
              { label: 'All Sources', value: '' },
              { label: 'PDFs', value: 'pdf' },
              { label: 'Word Docs', value: 'docx' },
              { label: 'Notes', value: 'notes' },
              { label: 'GitHub Repos', value: 'github' },
              { label: 'YouTube Transcripts', value: 'youtube' },
            ].map((opt) => (
              <button
                key={opt.label}
                type="button"
                onClick={() => setSourceType(opt.value)}
                className={`rounded px-2.5 py-1 transition-colors ${
                  sourceType === opt.value
                    ? 'bg-indigo-600/15 text-indigo-400 font-semibold border border-indigo-500/20'
                    : 'hover:bg-slate-900'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      </form>

      {/* Results Space */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center p-12 text-slate-500">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent mb-3"></div>
            <p className="text-sm">Retrieving matching vectors...</p>
          </div>
        ) : results.length > 0 ? (
          results.map((res, idx) => (
            <Card key={idx} className="space-y-3 border-slate-900">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-indigo-400" />
                  <span className="text-sm font-bold text-slate-200">{res.filename}</span>
                  {res.page && <span className="text-xs text-slate-500">• Page {res.page}</span>}
                  <span className="text-xs text-slate-500">• Chunk {res.chunk_number}</span>
                </div>
                <div className="rounded bg-indigo-500/10 px-2 py-0.5 text-xs font-semibold text-indigo-400 border border-indigo-500/20">
                  {(res.similarity_score * 100).toFixed(1)}% match
                </div>
              </div>
              <p className="text-sm text-slate-400 leading-relaxed italic bg-slate-900/10 p-3 rounded-lg border border-slate-900/40">
                "...{res.preview_snippet}..."
              </p>
            </Card>
          ))
        ) : searched ? (
          <div className="flex flex-col items-center justify-center p-12 text-center text-slate-500">
            <AlertTriangle className="h-8 w-8 mb-3 text-slate-650" />
            <p className="text-sm">No vector chunks matched your search parameters.</p>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center p-16 text-center text-slate-500">
            <Database className="h-10 w-10 mb-4 text-slate-700 animate-pulse" />
            <h3 className="text-sm font-bold text-slate-350">Vector Search Space Ready</h3>
            <p className="text-xs text-slate-500 max-w-xs mt-1">
              Type queries to search concepts directly across all documents.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
export default SearchPage;
