import React, { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Search, SlidersHorizontal, Calendar } from 'lucide-react';
import { Button } from '../components/ui/Button';

export const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) return;
    
    // Mock result for Phase 1
    setResults([
      {
        filename: 'AWS_Solutions_Architect.pdf',
        page: 4,
        similarity: 0.892,
        snippet: 'Amazon S3 provides a highly durable and secure object storage service that scales to accommodate arbitrary payloads...',
      },
    ]);
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 sm:text-3xl">Semantic Search</h1>
        <p className="mt-1.5 text-sm text-slate-400">
          Query your vector database directly and find exact source references.
        </p>
      </div>

      {/* Query Bar */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search keywords or sentences..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full rounded-lg border border-slate-900 bg-slate-900/40 py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none"
          />
        </div>
        <Button type="submit">Search</Button>
      </form>

      {/* Results Space */}
      <div className="space-y-4">
        {results.length > 0 ? (
          results.map((res, idx) => (
            <Card key={idx} className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-slate-200">{res.filename}</span>
                  <span className="text-xs text-slate-500">• Page {res.page}</span>
                </div>
                <div className="rounded bg-indigo-500/10 px-2 py-0.5 text-xs font-semibold text-indigo-400 border border-indigo-500/20">
                  {(res.similarity * 100).toFixed(1)}% match
                </div>
              </div>
              <p className="text-sm text-slate-400 italic">
                "...{res.snippet}..."
              </p>
            </Card>
          ))
        ) : (
          <div className="flex flex-col items-center justify-center p-12 text-center text-slate-500">
            <Search className="h-8 w-8 mb-3 text-slate-600" />
            <p className="text-sm">Type a query to search semantic embeddings</p>
          </div>
        )}
      </div>
    </div>
  );
};
