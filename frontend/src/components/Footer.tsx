import React from 'react';
import { HeartHandshake, Database, ShieldCheck, Sparkles } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-900 text-slate-400 text-sm mt-auto border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-3">
              <div className="h-8 w-8 rounded-lg bg-forest-600 flex items-center justify-center text-white">
                <HeartHandshake className="h-5 w-5" />
              </div>
              <span className="font-extrabold text-white text-lg">
                Community<span className="text-forest-400">Rescue</span> Network
              </span>
            </div>
            <p className="text-slate-400 text-xs sm:text-sm max-w-md leading-relaxed">
              Bridging restaurants, university messes, NGOs, and dedicated volunteers to eliminate surplus food waste and feed local communities before expiration.
            </p>
            <div className="mt-4 flex items-center gap-3 text-xs text-slate-500">
              <span className="flex items-center gap-1.5 bg-slate-800/80 px-2.5 py-1 rounded-md text-emerald-400 border border-emerald-500/20">
                <Database className="h-3.5 w-3.5" /> MySQL / XAMPP Connected
              </span>
              <span className="flex items-center gap-1.5 bg-slate-800/80 px-2.5 py-1 rounded-md text-slate-300 border border-slate-700">
                <ShieldCheck className="h-3.5 w-3.5" /> 100% Local Run
              </span>
            </div>
          </div>

          <div>
            <h4 className="text-xs uppercase font-bold text-slate-200 tracking-wider mb-3">Roles & Access</h4>
            <ul className="space-y-2 text-xs">
              <li><span className="text-slate-400 hover:text-white transition">Food Donors (Restaurants/Messes)</span></li>
              <li><span className="text-slate-400 hover:text-white transition">Registered NGO Partners</span></li>
              <li><span className="text-slate-400 hover:text-white transition">Community Volunteers</span></li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs uppercase font-bold text-slate-200 tracking-wider mb-3">DBMS Architecture</h4>
            <ul className="space-y-2 text-xs">
              <li>3NF Relational Normalization</li>
              <li>Row-Level Locking Concurrency</li>
              <li>Automated Dynamic Expiry Engine</li>
              <li>Full Audit Trail Delivery Logs</li>
            </ul>
          </div>
        </div>

        <div className="pt-6 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
          <p>© {new Date().getFullYear()} Community Food Rescue Network. Local Windows Academic Edition.</p>
          <div className="flex items-center gap-2 text-slate-400">
            <Sparkles className="h-4 w-4 text-forest-400" />
            <span>Zero Food Waste Mission</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

