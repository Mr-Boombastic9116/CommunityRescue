import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { AIAssistantDrawer } from './AIAssistantDrawer';
import { Sparkles } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user } = useAuth();
  const [isAIDrawerOpen, setIsAIDrawerOpen] = useState(false);

  return (
    <div className="flex-1 flex flex-col min-h-0 bg-slate-50">
      <div className="flex-1 flex min-h-0">
        {user && (
          <div className="hidden lg:block shrink-0">
            <Sidebar onOpenAIDrawer={() => setIsAIDrawerOpen(true)} />
          </div>
        )}
        <div className="flex-1 min-w-0 flex flex-col overflow-y-auto">
          <div className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
            {children}
          </div>
        </div>
      </div>

      {/* Floating AI Button */}
      {user && (
        <button
          type="button"
          onClick={() => setIsAIDrawerOpen(true)}
          className="fixed bottom-6 right-6 z-40 flex items-center gap-2.5 px-4 py-3 bg-gradient-to-r from-forest-800 to-forest-900 text-white font-bold text-sm rounded-full shadow-xl hover:shadow-2xl hover:scale-105 active:scale-95 transition-all border border-emerald-400/30 group"
          title="Open Gemma 4 Assistant"
        >
          <div className="p-1 rounded-full bg-emerald-500/20 text-emerald-300">
            <Sparkles className="w-4 h-4 animate-spin-slow group-hover:rotate-45 transition-transform" />
          </div>
          <span>Gemma 4 AI</span>
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        </button>
      )}

      {/* AI Assistant Drawer */}
      <AIAssistantDrawer
        isOpen={isAIDrawerOpen}
        onClose={() => setIsAIDrawerOpen(false)}
      />
    </div>
  );
};

export default Layout;

