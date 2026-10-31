import React, { useState, useEffect, useRef } from 'react';
import { 
  Bot, 
  Send, 
  X, 
  Sparkles, 
  Minimize2, 
  Maximize2, 
  RefreshCw, 
  ShieldCheck, 
  HelpCircle,
  MessageSquare
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { sendAIChatMessage, getAIStatus } from '../api/client';
import { ChatMessage, AIStatus } from '../types';

interface AIAssistantDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AIAssistantDrawer: React.FC<AIAssistantDrawerProps> = ({ isOpen, onClose }) => {
  const { user, role } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiStatus, setAiStatus] = useState<AIStatus | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Suggested prompts per role
  const suggestions: Record<string, string[]> = {
    donor: [
      'What are FSSAI safety limits for cooked rice and curry?',
      'How does partial quantity reservation work for my donations?',
      'Best packaging practices for hot cooked food',
    ],
    ngo: [
      'What donations are expiring soonest today?',
      'Can our NGO request only 15 kg out of a 50 kg donation?',
      'Safe storage guidelines for dairy and paneer',
    ],
    volunteer: [
      'Which pickup should I prioritize first right now?',
      'Safety checklist before accepting cooked food',
      'How to log food collection when at donor address',
    ],
  };

  const currentSuggestions = (role && suggestions[role]) || [
    'How does this food rescue network work?',
    'What are the food safety rules?',
    'How do I claim or request food?',
  ];

  useEffect(() => {
    if (isOpen) {
      getAIStatus()
        .then((res) => setAiStatus(res))
        .catch(() => setAiStatus({ status: 'online', model: 'gemma-4-26b-a4b-it', provider: 'google_genai' }));

      if (messages.length === 0) {
        setMessages([
          {
            sender: 'assistant',
            content: `Hello ${user?.name || 'there'}! I am **Gemma 4**, your intelligent food rescue assistant. How can I assist your ${role ? role.toUpperCase() : 'rescue'} workflow today?`,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          },
        ]);
      }
    }
  }, [isOpen, user, role]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (messageText?: string) => {
    const textToSend = messageText || input;
    if (!textToSend.trim() || loading) return;

    const userMsg: ChatMessage = {
      sender: 'user',
      content: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // Build conversation history for API
      const history = messages.map((m) => ({
        role: m.sender === 'user' ? 'user' : 'model',
        content: m.content,
      }));

      const res = await sendAIChatMessage(textToSend, history, {
        role,
        user_name: user?.name,
      });

      const aiMsg: ChatMessage = {
        sender: 'assistant',
        content: res.reply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        sender: 'assistant',
        content: `I encountered an issue connecting to the AI model. (${err?.message || 'Offline fallback active'}). Please try again.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white shadow-2xl flex flex-col border-l border-slate-200 animate-in slide-in-from-right duration-300">
      {/* Drawer Header */}
      <div className="px-5 py-4 bg-gradient-to-r from-forest-800 to-forest-900 text-white flex items-center justify-between shadow-md">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-forest-700/80 text-emerald-300 border border-forest-600/50">
            <Sparkles className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-extrabold text-base tracking-tight">Gemma 4 Assistant</h3>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-200 border border-emerald-400/30">
                Hosted AI
              </span>
            </div>
            <p className="text-xs text-forest-200 mt-0.5 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
              gemma-4-26b-a4b-it • Zero Hallucination
            </p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-forest-200 hover:text-white hover:bg-forest-700/50 transition"
          aria-label="Close Assistant"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/70">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
                msg.sender === 'user'
                  ? 'bg-forest-700 text-white rounded-br-none'
                  : 'bg-white text-slate-800 border border-slate-200/80 rounded-bl-none'
              }`}
            >
              <div className="whitespace-pre-line prose prose-sm max-w-none">
                {msg.content}
              </div>
            </div>
            <span className="text-[10px] text-slate-400 mt-1 px-1">{msg.timestamp}</span>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-slate-500 text-xs py-2 px-3 bg-white rounded-xl border border-slate-200 w-fit">
            <RefreshCw className="w-3.5 h-3.5 animate-spin text-forest-700" />
            <span>Gemma 4 is analyzing your request...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts */}
      <div className="px-4 py-2.5 bg-slate-100/90 border-t border-slate-200">
        <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1.5 flex items-center gap-1">
          <HelpCircle className="w-3 h-3 text-forest-600" />
          Suggested Quick Inquiries
        </p>
        <div className="flex flex-wrap gap-1.5">
          {currentSuggestions.map((prompt, index) => (
            <button
              key={index}
              onClick={() => handleSend(prompt)}
              className="text-xs bg-white text-forest-900 border border-forest-200 hover:border-forest-500 hover:bg-forest-50 px-2.5 py-1 rounded-lg transition text-left truncate max-w-full"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="p-3 bg-white border-t border-slate-200 flex items-center gap-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={`Ask Gemma 4 anything about food safety, tasks...`}
          disabled={loading}
          className="flex-1 px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-forest-600 focus:bg-white transition"
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="p-2.5 rounded-xl bg-forest-700 text-white hover:bg-forest-800 disabled:opacity-50 transition shadow-sm"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};

export default AIAssistantDrawer;

