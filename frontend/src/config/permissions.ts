import { UserRole } from '../types';

export const ROLE_DONOR: UserRole = 'donor';
export const ROLE_NGO: UserRole = 'ngo';
export const ROLE_VOLUNTEER: UserRole = 'volunteer';

export interface RoutePermission {
  path: string;
  allowedRoles: UserRole[];
  label: string;
}

export const ROUTE_PERMISSIONS: RoutePermission[] = [
  // Donor routes
  { path: '/donor/dashboard', allowedRoles: ['donor'], label: 'Overview' },
  { path: '/donor/donations/create', allowedRoles: ['donor'], label: 'Create Donation' },
  { path: '/donor/donations', allowedRoles: ['donor'], label: 'My Donations' },
  { path: '/donor/allocations', allowedRoles: ['donor'], label: 'Quantity Allocation' },
  { path: '/donor/expiry-alerts', allowedRoles: ['donor'], label: 'Expiry & FSSAI Alerts' },

  // NGO routes
  { path: '/ngo/dashboard', allowedRoles: ['ngo'], label: 'Overview' },
  { path: '/ngo/browse', allowedRoles: ['ngo'], label: 'Explore Food' },
  { path: '/ngo/requests', allowedRoles: ['ngo'], label: 'My Requests' },
  { path: '/ngo/allocations', allowedRoles: ['ngo'], label: 'Quantity Allocation' },
  { path: '/ngo/expiry-alerts', allowedRoles: ['ngo'], label: 'Expiry & FSSAI Alerts' },

  // Volunteer routes
  { path: '/volunteer/dashboard', allowedRoles: ['volunteer'], label: 'Overview' },
  { path: '/volunteer/tasks', allowedRoles: ['volunteer'], label: 'Available Tasks' },
  { path: '/volunteer/assigned', allowedRoles: ['volunteer'], label: 'My Assignments' },
  { path: '/volunteer/history', allowedRoles: ['volunteer'], label: 'Delivery History' },
  { path: '/volunteer/expiry-alerts', allowedRoles: ['volunteer'], label: 'Expiry & FSSAI Alerts' },

  // Shared routes
  { path: '/profile', allowedRoles: ['donor', 'ngo', 'volunteer'], label: 'Profile & Settings' },
  { path: '/ai-assistant', allowedRoles: ['donor', 'ngo', 'volunteer'], label: 'AI Assistant' },
];

export const isRouteAllowed = (path: string, role?: UserRole | null): boolean => {
  if (!role) return false;
  const match = ROUTE_PERMISSIONS.find((rp) => path.startsWith(rp.path));
  if (!match) return true; // public or unlisted
  return match.allowedRoles.includes(role);
};

export const canPerformAction = (
  action: 'create_donation' | 'request_food' | 'claim_task' | 'cancel_donation' | 'cancel_request',
  role?: UserRole | null
): boolean => {
  if (!role) return false;
  switch (action) {
    case 'create_donation':
    case 'cancel_donation':
      return role === 'donor';
    case 'request_food':
    case 'cancel_request':
      return role === 'ngo';
    case 'claim_task':
      return role === 'volunteer';
    default:
      return false;
  }
};

