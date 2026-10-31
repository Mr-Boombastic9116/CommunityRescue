import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { Layout } from './components/Layout';
import { ProtectedRoute } from './components/ProtectedRoute';

// Public Pages
import { LandingPage } from './pages/LandingPage';
import { AboutPage } from './pages/AboutPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { UnauthorizedPage } from './pages/UnauthorizedPage';
import { NotFoundPage } from './pages/NotFoundPage';

// Donor Pages
import { DonorDashboard } from './pages/donor/DonorDashboard';
import { CreateDonation } from './pages/donor/CreateDonation';
import { EditDonation } from './pages/donor/EditDonation';
import { MyDonations } from './pages/donor/MyDonations';
import { DonationDetail } from './pages/donor/DonationDetail';

// NGO Pages
import { NGODashboard } from './pages/ngo/NGODashboard';
import { BrowseFood } from './pages/ngo/BrowseFood';
import { MyRequests } from './pages/ngo/MyRequests';
import { RequestDetail } from './pages/ngo/RequestDetail';

// Volunteer Pages
import { VolunteerDashboard } from './pages/volunteer/VolunteerDashboard';
import { AvailableTasks } from './pages/volunteer/AvailableTasks';
import { AssignedTasks } from './pages/volunteer/AssignedTasks';
import { DeliveryHistory } from './pages/volunteer/DeliveryHistory';

// Shared & AI Pages
import { ProfileSettings } from './pages/shared/ProfileSettings';
import { QuantityAllocationPage } from './pages/shared/QuantityAllocationPage';
import { ExpiryAlertsPage } from './pages/shared/ExpiryAlertsPage';
import { AIAssistantPage } from './pages/shared/AIAssistantPage';

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800">
          <Navbar />
          <Layout>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/browse" element={<BrowseFood />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/unauthorized" element={<UnauthorizedPage />} />

              {/* Shared Authenticated Routes */}
              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <ProfileSettings />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/ai-assistant"
                element={
                  <ProtectedRoute>
                    <AIAssistantPage />
                  </ProtectedRoute>
                }
              />

              {/* Donor Routes */}
              <Route
                path="/donor/dashboard"
                element={
                  <ProtectedRoute allowedRoles={['donor']}>
                    <DonorDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/donor/donations"
                element={
                  <ProtectedRoute allowedRoles={['donor']}>
                    <MyDonations />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/donor/donations/create"
                element={
                  <ProtectedRoute allowedRoles={['donor']}>
                    <CreateDonation />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/donor/donations/:batchId"
                element={
                  <ProtectedRoute allowedRoles={['donor']}>
                    <DonationDetail />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/donor/donations/:batchId/edit"
                element={
                  <ProtectedRoute allowedRoles={['donor']}>
                    <EditDonation />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/donor/allocations"
                element={
                  <ProtectedRoute allowedRoles={['donor']}>
                    <QuantityAllocationPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/donor/expiry-alerts"
                element={
                  <ProtectedRoute allowedRoles={['donor']}>
                    <ExpiryAlertsPage />
                  </ProtectedRoute>
                }
              />

              {/* NGO Routes */}
              <Route
                path="/ngo/dashboard"
                element={
                  <ProtectedRoute allowedRoles={['ngo']}>
                    <NGODashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/ngo/browse"
                element={
                  <ProtectedRoute allowedRoles={['ngo']}>
                    <BrowseFood />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/ngo/requests"
                element={
                  <ProtectedRoute allowedRoles={['ngo']}>
                    <MyRequests />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/ngo/requests/:requestId"
                element={
                  <ProtectedRoute allowedRoles={['ngo']}>
                    <RequestDetail />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/ngo/allocations"
                element={
                  <ProtectedRoute allowedRoles={['ngo']}>
                    <QuantityAllocationPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/ngo/expiry-alerts"
                element={
                  <ProtectedRoute allowedRoles={['ngo']}>
                    <ExpiryAlertsPage />
                  </ProtectedRoute>
                }
              />

              {/* Volunteer Routes */}
              <Route
                path="/volunteer/dashboard"
                element={
                  <ProtectedRoute allowedRoles={['volunteer']}>
                    <VolunteerDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/volunteer/tasks"
                element={
                  <ProtectedRoute allowedRoles={['volunteer']}>
                    <AvailableTasks />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/volunteer/assigned"
                element={
                  <ProtectedRoute allowedRoles={['volunteer']}>
                    <AssignedTasks />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/volunteer/history"
                element={
                  <ProtectedRoute allowedRoles={['volunteer']}>
                    <DeliveryHistory />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/volunteer/expiry-alerts"
                element={
                  <ProtectedRoute allowedRoles={['volunteer']}>
                    <ExpiryAlertsPage />
                  </ProtectedRoute>
                }
              />

              {/* Catch-all 404 */}
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </Layout>
          <Footer />
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
