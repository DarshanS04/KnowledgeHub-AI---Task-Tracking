import React, { useState } from 'react';
import { Card } from '../components/ui/Card';
import { MessageSquare, Send, BookOpen, User } from 'lucide-react';
import { Button } from '../components/ui/Button';

export const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([
    { role: 'assistant', content: "Hello! Ask me any questions referencing your uploaded files, and I'll answer them with proper page citations." },
  ]);
  const [input, setInput] = useState('');

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setMessages([...messages, { role: 'user', content: input }]);
    setInput('');
    
    // Stub reply after a delay
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: "I received your query. In the next phase, we'll connect this window to the Google Gemini LLM and retrieve vector matches from Qdrant.",
        },
      ]);
    }, 1000);
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col gap-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 sm:text-3xl">Chat Workspace</h1>
        <p className="mt-1.5 text-sm text-slate-400">Ask questions and see citations.</p>
      </div>

      <Card className="flex-1 flex flex-col p-4 bg-slate-950/20 border-slate-900 overflow-hidden">
        {/* Messages space */}
        <div className="flex-1 overflow-y-auto space-y-4 pr-2">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex gap-3 max-w-[85%] ${
                msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''
              }`}
            >
              <div className={`flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full text-xs font-bold ${
                msg.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-300'
              }`}>
                {msg.role === 'user' ? <User className="h-4 w-4" /> : <BookOpen className="h-4 w-4 text-indigo-400" />}
              </div>
              <div className={`rounded-xl px-4 py-2.5 text-sm leading-relaxed ${
                msg.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-slate-900 border border-slate-900 text-slate-300'
              }`}>
                {msg.content}
              </div>
            </div>
          ))}
        </div>

        {/* Input form */}
        <form onSubmit={handleSend} className="mt-4 flex gap-2 pt-4 border-t border-slate-900">
          <input
            type="text"
            placeholder="Type your question about documents..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 rounded-lg border border-slate-900 bg-slate-900/40 px-4 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none"
          />
          <Button type="submit">
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </Card>
    </div>
  );
};
