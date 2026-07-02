import React, { useEffect, useState } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { FileText, Trash2, Calendar, Database, RefreshCcw, HardDrive } from 'lucide-react';
import { documentsApi } from '../api/documents';
import { DocumentResponse } from '../types';

export const DocumentsPage: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalDocs, setTotalDocs] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchDocuments = async (pageNum = 1) => {
    setIsLoading(true);
    try {
      const response = await documentsApi.listDocuments(pageNum, 10);
      setDocuments(response.data);
      setPage(response.meta.page);
      setTotalPages(response.meta.pages);
      setTotalDocs(response.meta.total);
    } catch (e) {
      console.error('Failed to fetch documents:', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments(1);
  }, []);

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this document? All associated vector embeddings will be removed.')) {
      return;
    }
    setDeletingId(id);
    try {
      await documentsApi.deleteDocument(id);
      setDocuments((prev) => prev.filter((doc) => doc.id !== id));
      setTotalDocs((prev) => prev - 1);
    } catch (e) {
      console.error('Failed to delete document:', e);
    } finally {
      setDeletingId(null);
    }
  };

  const getSourceIcon = (sourceType: string) => {
    switch (sourceType) {
      case 'pdf':
        return 'PDF';
      case 'docx':
        return 'DOC';
      case 'notes':
        return 'NOTE';
      case 'github':
        return 'GIT';
      case 'youtube':
        return 'YT';
      default:
        return 'TXT';
    }
  };

  const formatSize = (bytes?: number) => {
    if (!bytes) return 'N/A';
    if (bytes < 1024) return `${bytes} B`;
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    return `${(kb / 1024).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 sm:text-3xl">Ingested Knowledge</h1>
          <p className="mt-1.5 text-sm text-slate-400">
            Audit, refresh, or remove ingested documents inside your RAG database collection.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => fetchDocuments(page)} className="gap-2">
          <RefreshCcw className="h-4 w-4" /> Refresh
        </Button>
      </div>

      <Card className="border-slate-900">
        {isLoading && documents.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-12 text-slate-500">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent mb-3"></div>
            <p className="text-sm">Loading documents...</p>
          </div>
        ) : documents.length > 0 ? (
          <div className="space-y-6">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="border-b border-slate-800 text-xs uppercase text-slate-500 font-bold">
                  <tr>
                    <th className="py-4 px-3">Name</th>
                    <th className="py-4 px-3">Type</th>
                    <th className="py-4 px-3">Size</th>
                    <th className="py-4 px-3">Vector Chunks</th>
                    <th className="py-4 px-3">Status</th>
                    <th className="py-4 px-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-900">
                  {documents.map((doc) => (
                    <tr key={doc.id} className="hover:bg-slate-900/10">
                      <td className="py-4 px-3 font-semibold text-slate-200 truncate max-w-[200px]">
                        {doc.original_filename}
                      </td>
                      <td className="py-4 px-3">
                        <span className="inline-flex items-center rounded bg-slate-900 px-2 py-0.5 text-xs font-semibold text-indigo-400 border border-slate-800">
                          {getSourceIcon(doc.source_type)}
                        </span>
                      </td>
                      <td className="py-4 px-3 text-slate-400">
                        {formatSize(doc.file_size)}
                      </td>
                      <td className="py-4 px-3 font-medium">
                        {doc.total_chunks}
                      </td>
                      <td className="py-4 px-3">
                        <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold ${
                          doc.status === 'completed'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : doc.status === 'failed'
                            ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                            : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 animate-pulse'
                        }`}>
                          {doc.status}
                        </span>
                      </td>
                      <td className="py-4 px-3 text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          disabled={deletingId === doc.id}
                          onClick={() => handleDelete(doc.id)}
                          className="text-rose-500 hover:bg-rose-950/20"
                        >
                          {deletingId === doc.id ? (
                            <div className="h-4 w-4 animate-spin rounded-full border-2 border-rose-500 border-t-transparent"></div>
                          ) : (
                            <Trash2 className="h-4 w-4" />
                          )}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between border-t border-slate-850 pt-4">
                <p className="text-xs text-slate-400">
                  Showing page <span className="font-semibold text-slate-200">{page}</span> of{' '}
                  <span className="font-semibold text-slate-200">{totalPages}</span> ({totalDocs} documents total)
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page === 1}
                    onClick={() => fetchDocuments(page - 1)}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page === totalPages}
                    onClick={() => fetchDocuments(page + 1)}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center p-16 text-center text-slate-500">
            <HardDrive className="h-10 w-10 mb-4 text-slate-700" />
            <h3 className="text-sm font-bold text-slate-300">No knowledge indexed yet</h3>
            <p className="text-xs text-slate-500 max-w-xs mt-1">
              Once you upload files or point to code repositories, they will appear here.
            </p>
          </div>
        )}
      </Card>
    </div>
  );
};
export default DocumentsPage;
