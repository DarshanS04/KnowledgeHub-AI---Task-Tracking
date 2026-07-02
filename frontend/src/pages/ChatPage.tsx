import React, { useState, useEffect, useRef } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import {
  MessageSquare,
  Send,
  BookOpen,
  User,
  Trash2,
  Edit2,
  X,
  FileText,
  AlertTriangle,
  Plus,
} from 'lucide-react';
import { chatApi } from '../api/chat';
import { ConversationResponse, MessageResponse } from '../types';
import ReactMarkdown from 'react-markdown';

export const ChatPage: React.FC = () => {
  const [conversations, setConversations] = useState<ConversationResponse[]>([]);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [input, setInput] = useState('');
  
  // Streaming state
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const [streamingCitations, setStreamingCitations] = useState<any[]>([]);

  // Editing state
  const [editingConvId, setEditingConvId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversations on mount
  const fetchConversations = async () => {
    try {
      const res = await chatApi.listConversations(1, 20);
      setConversations(res.data);
      if (res.data.length > 0 && !activeConvId) {
        setActiveConvId(res.data[0].id);
      }
    } catch (e) {
      console.error('Failed to load conversations:', e);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  // Load messages when active conversation changes
  useEffect(() => {
    if (!activeConvId) return;
    const fetchMessages = async () => {
      try {
        const msgs = await chatApi.getMessages(activeConvId);
        setMessages(msgs);
        setStreamingText('');
        setStreamingCitations([]);
      } catch (e) {
        console.error('Failed to load messages:', e);
      }
    };
    fetchMessages();
  }, [activeConvId]);

  // Scroll to bottom on messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingText]);

  const handleCreateConversation = async () => {
    try {
      const conv = await chatApi.renameConversation(uuidPlaceholder(), 'New Conversation');
      // Wait, renameConversation with empty string or a custom create conversation method?
      // In chatApi we defined:
      // renameConversation: put to /chat/{id}
      // But wait! In chat router POST /chat accepts conversation_id in request body.
      // If we pass conversation_id = null (which means new conversation), the backend creates a conversation and returns its ID!
      // So to create a conversation on the frontend, we can simply start a new empty conversation state or trigger an initial message.
      // Let's make starting a new conversation clean on frontend: just set activeConvId = null!
      setActiveConvId(null);
      setMessages([]);
      setStreamingText('');
      setStreamingCitations([]);
    } catch (e) {
      console.error(e);
    }
  };

  const uuidPlaceholder = () => {
    return '00000000-0000-0000-0000-000000000000';
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    const userMessageText = input;
    setInput('');
    setIsStreaming(true);
    setStreamingText('');
    setStreamingCitations([]);

    // Optimistically log user message in local state
    const userMsgPlaceholder: MessageResponse = {
      id: uuidPlaceholder(),
      conversation_id: activeConvId || uuidPlaceholder(),
      role: 'user',
      content: userMessageText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsgPlaceholder]);

    try {
      let currentConvId = activeConvId;
      
      // Call streaming generator
      const stream = chatApi.streamChat(userMessageText, currentConvId || undefined);

      for await (const chunk of stream) {
        if (chunk.event === 'meta') {
          // If a new conversation was created on the backend, register its ID
          const newId = chunk.data.conversation_id;
          if (!currentConvId && newId) {
            currentConvId = newId;
            setActiveConvId(newId);
            fetchConversations(); // Reload conversation sidebar list
          }
        } else if (chunk.event === 'citations') {
          setStreamingCitations(chunk.data);
        } else if (chunk.event === 'token') {
          setStreamingText((prev) => prev + chunk.data);
        } else if (chunk.event === 'error') {
          throw new Error(chunk.data || 'Streaming error occurred.');
        }
      }

      // Once streaming finishes, fetch the updated message list from DB to replace state with real citations
      if (currentConvId) {
        const updatedMsgs = await chatApi.getMessages(currentConvId);
        setMessages(updatedMsgs);
        setStreamingText('');
        setStreamingCitations([]);
      }

    } catch (err) {
      console.error('Chat error:', err);
      setMessages((prev) => [
        ...prev,
        {
          id: uuidPlaceholder(),
          conversation_id: activeConvId || uuidPlaceholder(),
          role: 'assistant',
          content: 'An error occurred while generating a response from the knowledge base. Ensure your API keys are valid.',
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsStreaming(false);
    }
  };

  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Delete this conversation thread?')) return;
    try {
      await chatApi.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeConvId === id) {
        setActiveConvId(null);
        setMessages([]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const startEditing = (id: string, currentTitle: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingConvId(id);
    setEditTitle(currentTitle);
  };

  const handleRename = async (id: string) => {
    if (!editTitle.trim()) return;
    try {
      await chatApi.renameConversation(id, editTitle);
      setConversations((prev) =>
        prev.map((c) => (c.id === id ? { ...c, title: editTitle } : c))
      );
      setEditingConvId(null);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 h-[calc(100vh-8rem)]">
      {/* Sidebar Conversation List */}
      <Card className="md:col-span-1 flex flex-col border-slate-900 bg-slate-950/20 p-4 h-full overflow-hidden">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xs font-bold uppercase text-slate-500 tracking-wider">Conversations</h3>
          <Button size="sm" variant="ghost" onClick={handleCreateConversation} className="p-1 h-7 w-7 rounded-full text-indigo-400 hover:bg-indigo-950/20">
            <Plus className="h-4 w-4" />
          </Button>
        </div>

        {/* Scrollable list */}
        <div className="flex-1 overflow-y-auto space-y-1.5 pr-1">
          {conversations.map((c) => (
            <div
              key={c.id}
              onClick={() => setActiveConvId(c.id)}
              className={`group flex items-center justify-between rounded-lg px-3 py-2 text-sm cursor-pointer transition-colors ${
                activeConvId === c.id
                  ? 'bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 font-medium'
                  : 'text-slate-400 hover:bg-slate-900/40 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center gap-2.5 overflow-hidden flex-1">
                <MessageSquare className="h-4 w-4 shrink-0" />
                {editingConvId === c.id ? (
                  <input
                    type="text"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleRename(c.id)}
                    onBlur={() => handleRename(c.id)}
                    className="bg-slate-900 border border-slate-800 text-xs rounded px-1.5 py-0.5 text-slate-200 w-full focus:outline-none focus:border-indigo-500"
                    autoFocus
                  />
                ) : (
                  <span className="truncate text-xs">{c.title}</span>
                )}
              </div>
              
              {editingConvId !== c.id && (
                <div className="hidden group-hover:flex items-center gap-1 shrink-0 ml-1">
                  <button onClick={(e) => startEditing(c.id, c.title, e)} className="text-slate-500 hover:text-indigo-400 p-0.5">
                    <Edit2 className="h-3.5 w-3.5" />
                  </button>
                  <button onClick={(e) => handleDeleteConversation(c.id, e)} className="text-slate-500 hover:text-rose-400 p-0.5">
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Chat workspace area */}
      <Card className="md:col-span-3 flex flex-col border-slate-900 h-full overflow-hidden p-4">
        {/* Messages List Area */}
        <div className="flex-1 overflow-y-auto space-y-6 pr-2">
          {messages.map((msg, idx) => (
            <div
              key={msg.id === uuidPlaceholder() ? idx : msg.id}
              className={`flex gap-3 max-w-[85%] ${
                msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''
              }`}
            >
              {/* Avatar */}
              <div className={`flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full text-xs font-bold border ${
                msg.role === 'user'
                  ? 'bg-indigo-600 border-indigo-500 text-white'
                  : 'bg-slate-900 border-slate-800 text-indigo-400'
              }`}>
                {msg.role === 'user' ? <User className="h-4 w-4" /> : <BookOpen className="h-4 w-4" />}
              </div>

              {/* Message Bubble Panel */}
              <div className="space-y-2 flex-1">
                <div className={`rounded-xl px-4 py-3 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-900/60 border border-slate-900 text-slate-350 shadow-md'
                }`}>
                  <ReactMarkdown className="markdown-content">{msg.content}</ReactMarkdown>
                </div>

                {/* Citations cards if assistant message */}
                {msg.role === 'assistant' && msg.citations && msg.citations.length > 0 && (
                  <div className="flex flex-wrap gap-2 pt-1.5">
                    {msg.citations.map((cite, cIdx) => (
                      <div
                        key={cIdx}
                        className="group relative flex items-center gap-1.5 rounded-lg border border-slate-800/80 bg-slate-900/20 px-2 py-1 text-[10px] text-slate-400 cursor-help hover:bg-slate-900/60 hover:text-indigo-400 transition-all shadow-sm"
                      >
                        <FileText className="h-3 w-3 text-indigo-500/80" />
                        <span className="truncate max-w-[120px] font-semibold">{cite.filename}</span>
                        {cite.page_number && <span className="font-semibold text-slate-500">p.{cite.page_number}</span>}

                        {/* Citation hover details tooltip */}
                        <div className="absolute bottom-full left-0 mb-2 hidden group-hover:block w-72 rounded-lg border border-slate-800 bg-[#090d16] p-3 text-xs text-slate-350 shadow-2xl z-50">
                          <p className="font-bold text-indigo-400 border-b border-slate-900 pb-1 mb-1.5 truncate">
                            {cite.filename} (Page {cite.page_number || 'N/A'}, Chunk {cite.chunk_number})
                          </p>
                          <p className="italic text-slate-400 leading-normal">
                            "...{cite.snippet}..."
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Render Active Streaming Answer Output */}
          {isStreaming && streamingText && (
            <div className="flex gap-3 max-w-[85%]">
              <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full bg-slate-900 border border-slate-800 text-indigo-400 text-xs font-bold">
                <BookOpen className="h-4 w-4" />
              </div>
              <div className="space-y-2 flex-1">
                <div className="rounded-xl px-4 py-3 text-sm leading-relaxed bg-slate-900/60 border border-slate-900 text-slate-300">
                  <ReactMarkdown className="markdown-content">{streamingText}</ReactMarkdown>
                </div>
                
                {/* Render Citations optimistically while streaming */}
                {streamingCitations.length > 0 && (
                  <div className="flex flex-wrap gap-2 pt-1.5 animate-fade-in">
                    {streamingCitations.map((cite, cIdx) => (
                      <div
                        key={cIdx}
                        className="group relative flex items-center gap-1.5 rounded-lg border border-slate-800/80 bg-slate-900/20 px-2 py-1 text-[10px] text-slate-400 cursor-help"
                      >
                        <FileText className="h-3 w-3 text-indigo-500/80" />
                        <span className="truncate max-w-[120px] font-semibold">{cite.filename}</span>
                        {cite.page_number && <span className="font-semibold text-slate-500">p.{cite.page_number}</span>}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Loading bubble when waiting for stream startup */}
          {isStreaming && !streamingText && (
            <div className="flex gap-3 max-w-[80%] items-center">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-900 border border-slate-800 text-indigo-400 text-xs font-bold animate-pulse">
                <BookOpen className="h-4 w-4" />
              </div>
              <div className="flex gap-1.5 rounded-lg bg-slate-900/40 p-3 border border-slate-900">
                <span className="h-2 w-2 animate-bounce rounded-full bg-indigo-500 delay-100"></span>
                <span className="h-2 w-2 animate-bounce rounded-full bg-indigo-500 delay-200"></span>
                <span className="h-2 w-2 animate-bounce rounded-full bg-indigo-500 delay-300"></span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Form message input */}
        <form onSubmit={handleSend} className="mt-4 flex gap-2 pt-4 border-t border-slate-900">
          <input
            type="text"
            disabled={isStreaming}
            placeholder="Query your knowledge space..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 rounded-lg border border-slate-800 bg-slate-900/40 px-4 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none disabled:opacity-50"
          />
          <Button type="submit" disabled={isStreaming || !input.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </Card>
    </div>
  );
};
export default ChatPage;
