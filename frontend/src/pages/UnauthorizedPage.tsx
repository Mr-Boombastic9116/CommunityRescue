import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, ArrowLeft } from 'lucide-react';

export const UnauthorizedPage: React.FC = () => {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center p-6 text-center">
      <div className="h-16 w-16 rounded-3xl bg-rose-50 text-rose-600 flex items-center justify-center mb-6 ring-8 ring-rose-50/50">
        <ShieldAlert className="h-8 w-8" />
      </div>
      <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mb-2">
        Access Restricted
      </h1>
      <p className="text-sm text-slate-600 max-w-md mb-8">
        You do not have the required role permissions to view or interact with this page.
      </p>
      <Link
        to="/"
        className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-forest-700 hover:bg-forest-800 text-white font-bold text-sm transition"
      >
        <ArrowLeft className="h-4 w-4" />
        Return to Home
      </Link>
    </div>
  );
};

