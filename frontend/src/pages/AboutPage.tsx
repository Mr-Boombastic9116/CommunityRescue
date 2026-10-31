import React from 'react';
import { 
  CheckCircle2, 
  Database, 
  ShieldCheck, 
  Clock, 
  ArrowRight,
  GitBranch,
  Lock,
  Layers
} from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto">
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mb-4">
          How Community Food Rescue Works
        </h1>
        <p className="text-base text-slate-600 leading-relaxed">
          An end-to-end relational platform designed to connect food donors, shelter organizations, and volunteer couriers in real time while enforcing database ACID properties and concurrency guarantees.
        </p>
      </div>

      {/* 14-Step Complete Pipeline */}
      <div className="bg-white rounded-3xl p-8 sm:p-10 border border-slate-200/80 shadow-sm">
        <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
          <Layers className="h-5 w-5 text-forest-700" />
          The Complete 14-Step Rescue Lifecycle
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs sm:text-sm">
          {[
            { step: '1', title: 'Donor Authentication', desc: 'Donor logs in via secure JWT authentication with hashed credentials.' },
            { step: '2', title: 'Food Donation Creation', desc: 'Donor specifies quantity, preparation time, expiry window, and pickup location.' },
            { step: '3', title: 'Backend Constraint Validation', desc: 'FastAPI and MySQL CHECK constraints ensure positive quantities and expiry > prep time.' },
            { step: '4', title: 'Persistent Storage', desc: 'Batch is recorded in MySQL InnoDB table `food_batches` with default status "available".' },
            { step: '5', title: 'Live Dashboard Propagation', desc: 'Batch appears immediately on the donor dashboard and live public feed.' },
            { step: '6', title: 'NGO Discovery', desc: 'Verified NGOs filter and search donations by category, urgency, and distance.' },
            { step: '7', title: 'NGO Request Placement', desc: 'NGO claims the batch, creating a record in `pickup_requests` and setting status to "requested".' },
            { step: '8', title: 'Transaction Logging', desc: 'Event is written to `delivery_logs` audit trail with performer and timestamp.' },
            { step: '9', title: 'Atomic Volunteer Task Claim', desc: 'Volunteer claims task using row locking (SELECT ... FOR UPDATE) preventing double-assignment.' },
            { step: '10', title: 'Status Transition to Assigned', desc: 'System marks request as "assigned", batch as "assigned", and alerts NGO and Donor.' },
            { step: '11', title: 'Physical Pickup Verification', desc: 'Volunteer arrives at donor address and clicks "Mark Collected", locking status to "collected".' },
            { step: '12', title: 'Safe Delivery Handover', desc: 'Volunteer completes drop-off at NGO facility and submits delivery completion notes.' },
            { step: '13', title: 'Automatic Status Finalization', desc: 'Request and Batch statuses transition to "delivered", updating donor and NGO impact counts.' },
            { step: '14', title: 'Full Audit Trail Delivery Log', desc: 'All state transitions and notes remain permanently verifiable in MySQL.' },
          ].map((item) => (
            <div key={item.step} className="flex gap-3 p-3.5 rounded-2xl bg-slate-50 border border-slate-100">
              <span className="flex h-7 w-7 items-center justify-center rounded-xl bg-forest-100 text-forest-800 font-bold text-xs flex-shrink-0">
                {item.step}
              </span>
              <div>
                <h4 className="font-bold text-slate-900">{item.title}</h4>
                <p className="text-slate-500 text-xs mt-0.5">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Concurrency and Expiry Architecture */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white rounded-3xl p-8 border border-slate-200/80 shadow-sm">
          <div className="h-10 w-10 rounded-2xl bg-amber-50 text-amber-700 flex items-center justify-center mb-4">
            <Lock className="h-5 w-5" />
          </div>
          <h3 className="text-lg font-bold text-slate-900 mb-2">
            Concurrency & Row Locking Control
          </h3>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
            In busy rescue networks, multiple volunteers might tap "Claim Assignment" at the exact same millisecond. 
            Our backend prevents race conditions by acquiring a row lock (<code className="bg-slate-100 px-1 py-0.5 rounded text-xs font-mono">with_for_update()</code>) on the pickup request within an explicit transaction.
            Only the first thread acquires the lock and transitions the task; subsequent concurrent attempts receive HTTP 409 Conflict.
          </p>
        </div>

        <div className="bg-white rounded-3xl p-8 border border-slate-200/80 shadow-sm">
          <div className="h-10 w-10 rounded-2xl bg-rose-50 text-rose-700 flex items-center justify-center mb-4">
            <Clock className="h-5 w-5" />
          </div>
          <h3 className="text-lg font-bold text-slate-900 mb-2">
            Automated Food Expiry Engine
          </h3>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
            A persistent asynchronous background loop checks all active food batches. 
            Any batch that passes its expiry timestamp before pickup is automatically flagged as <span className="font-semibold text-rose-700">Expired</span>, and pending requests are cancelled with notifications.
            Crucially, food that has already been collected by a volunteer or delivered is never invalidated.
          </p>
        </div>
      </div>
    </div>
  );
};

