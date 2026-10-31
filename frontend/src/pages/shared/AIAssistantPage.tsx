import React, { useState, useEffect, useRef } from 'react';
import { 
  Sparkles, 
  Send, 
  RefreshCw, 
  Bot, 
  User, 
  HelpCircle, 
  ShieldCheck, 
  CheckCircle2, 
  Copy, 
  Trash2,
  Cpu
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { sendAIChatMessage, getAIStatus } from '../../api/client';
import { ChatMessage, AIStatus } from '../../types';

export const AIAssistantPage: React.FC = () => {
  const { user, role } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiStatus, setAiStatus] = useState<AIStatus | null>(null);
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getAIStatus()
      .then((s) => setAiStatus(s))
      .catch(() => setAiStatus({ status: 'online', model: 'gemma-4-26b-a4b-it', provider: 'google_genai' }));

    setMessages([
      {
        sender: 'assistant',
        content: `👋 Hello **${user?.name || 'Partner'}**! I am **Gemma 4**, the intelligent AI assistant powering the Community Food Rescue Network.\n\nI have real-time access to the current donation database, FSSAI regulatory safety standards, and logistical routing parameters. How can I assist your ${role || 'community'} mission today?`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
  }, [user, role]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || input;
    if (!text.trim() || loading) return;

    const userMsg: ChatMessage = {
      sender: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const history = messages.map((m) => ({
        role: m.sender === 'user' ? 'user' : 'model',
        content: m.content,
      }));

      const res = await sendAIChatMessage(text, history);

      const aiMsg: ChatMessage = {
        sender: 'assistant',
        content: res.reply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        parsed_intent: res.parsed_intent,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          content: `⚠️ Failed to receive response from Gemma 4: ${err?.message || 'Offline fallback active'}. Please try asking again.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  const samplePrompts = [
    'What are the mandatory FSSAI safety time limits for hot cooked meals?',
    'How do I claim a partial 20 kg portion from a 50 kg surplus donation?',
    'What food batches in our area need urgent rescue right now?',
    'What packaging and hygiene measures should volunteers verify before pickup?',
  ];

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 bg-gradient-to-r from-forest-800 to-forest-900 text-white flex items-center justify-between shadow-md">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-forest-700/80 rounded-2xl border border-emerald-400/30 text-emerald-300">
            <Sparkles className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-extrabold text-lg tracking-tight">Gemma 4 AI Assistant Workspace</h2>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-200 border border-emerald-400/30">
                Hosted via Gemini API
              </span>
            </div>
            <p className="text-xs text-forest-200 mt-0.5 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              <span>Model: <strong className="font-mono text-emerald-100">{aiStatus?.model || 'gemma-4-26b-a4b-it'}</strong></span>
              <span>•</span>
              <span className="flex items-center gap-1 text-emerald-200">
                <ShieldCheck className="w-3.5 h-3.5" /> FSSAI-Curated Guardrails
              </span>
            </p>
          </div>
        </div>

        <button
          onClick={() => setMessages([])}
          className="p-2 text-forest-200 hover:text-white hover:bg-forest-700/50 rounded-xl transition"
          title="Clear Conversation"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50/60">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-3 ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
          >
            <div
              className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-sm ${
                msg.sender === 'user'
                  ? 'bg-forest-700 text-white'
                  : 'bg-emerald-600 text-white'
              }`}
            >
              {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div className={`max-w-2xl rounded-2xl p-4 shadow-sm ${
              msg.sender === 'user'
                ? 'bg-forest-700 text-white rounded-tr-none'
                : 'bg-white text-slate-800 border border-slate-200/80 rounded-tl-none'
            }`}>
              <div className="text-sm whitespace-pre-line leading-relaxed">
                {msg.content}
              </div>

              {msg.parsed_intent && (
                <div className="mt-2.5 pt-2 border-t border-slate-100 flex flex-wrap items-center gap-1.5 text-[10px]">
                  <span className="font-bold uppercase px-2 py-0.5 rounded-full bg-forest-50 text-forest-800 border border-forest-200">
                    🎯 Intent: {msg.parsed_intent.intent}
                  </span>
                  {msg.parsed_intent.main_entity && (
                    <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                      Entity: {msg.parsed_intent.main_entity}
                    </span>
                  )}
                  {msg.parsed_intent.action && (
                    <span className="px-2 py-0.5 rounded-full bg-blue-50 text-blue-700">
                      Action: {msg.parsed_intent.action}
                    </span>
                  )}
                  {msg.parsed_intent.quantity && (
                    <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700">
                      Qty: {msg.parsed_intent.quantity} {msg.parsed_intent.unit || ''}
                    </span>
                  )}
                </div>
              )}

              {msg.parsed_intent?.confirmation_required && (
                <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-xl space-y-2">
                  <p className="text-xs font-semibold text-amber-900">
                    ⚠️ {msg.parsed_intent.confirmation_prompt || 'Confirmation required for this action:'}
                  </p>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => handleSend('Yes, I confirm and authorize this action.')}
                      className="px-3 py-1 bg-forest-700 hover:bg-forest-800 text-white text-xs font-bold rounded-lg shadow-sm"
                    >
                      Confirm Action
                    </button>
                    <button
                      type="button"
                      onClick={() => handleSend('No, please cancel this action.')}
                      className="px-3 py-1 bg-slate-200 hover:bg-slate-300 text-slate-700 text-xs font-semibold rounded-lg"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
              <div className="mt-2 pt-2 border-t border-slate-100/30 flex items-center justify-between text-[10px] text-slate-400">
                <span>{msg.timestamp}</span>
                {msg.sender === 'assistant' && (
                  <button
                    onClick={() => copyToClipboard(msg.content, idx)}
                    className="flex items-center gap-1 text-slate-500 hover:text-slate-800 transition"
                  >
                    {copiedIdx === idx ? (
                      <>
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        <span className="text-emerald-600">Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
                        <span>Copy</span>
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-3 text-slate-500 text-xs py-3 px-4 bg-white rounded-2xl border border-slate-200 w-fit">
            <RefreshCw className="w-4 h-4 animate-spin text-forest-700" />
            <span>Gemma 4 is processing regulatory guidelines and community data...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Inquiries Footer */}
      <div className="px-6 py-2.5 bg-slate-100/90 border-t border-slate-200 flex items-center gap-2 overflow-x-auto">
        <span className="text-xs font-bold text-slate-500 shrink-0 flex items-center gap-1">
          <HelpCircle className="w-3.5 h-3.5 text-forest-700" /> Suggestions:
        </span>
        {samplePrompts.map((prompt, i) => (
          <button
            key={i}
            onClick={() => handleSend(prompt)}
            className="text-xs bg-white text-slate-700 border border-slate-200 hover:border-forest-500 hover:bg-forest-50 px-3 py-1.5 rounded-xl transition whitespace-nowrap"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Form Input */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="p-4 bg-white border-t border-slate-200 flex items-center gap-3"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Gemma 4 anything about food allocation, expiry limits, or logistics..."
          disabled={loading}
          className="flex-1 px-4 py-3 text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-forest-600 focus:bg-white transition"
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="px-6 py-3 rounded-xl bg-forest-700 hover:bg-forest-800 text-white font-bold text-sm disabled:opacity-50 transition flex items-center gap-2 shadow-sm"
        >
          <span>Send</span>
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};

export default AIAssistantPage;

