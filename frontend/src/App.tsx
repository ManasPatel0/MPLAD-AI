import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { ApiStatusModal } from './components/ApiStatusModal';
import { DashboardPage } from './pages/DashboardPage';
import { PlaceholderPage } from './pages/PlaceholderPage';
import { fetchHealthCheck, HealthCheckResult } from './services/api';

export const App: React.FC = () => {
  const [health, setHealth] = useState<HealthCheckResult | null>(null);
  const [isLoadingHealth, setIsLoadingHealth] = useState<boolean>(true);
  const [isHealthModalOpen, setIsHealthModalOpen] = useState<boolean>(false);

  const checkHealth = useCallback(async () => {
    setIsLoadingHealth(true);
    try {
      const res = await fetchHealthCheck();
      setHealth(res);
    } finally {
      setIsLoadingHealth(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    // Re-check periodically every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-slate-50 font-sans antialiased text-slate-900">
        {/* Left Navigation Sidebar */}
        <Sidebar />

        {/* Primary Content Container */}
        <div className="flex-1 flex flex-col min-w-0">
          <Header
            health={health}
            isLoadingHealth={isLoadingHealth}
            onRefreshHealth={checkHealth}
            onOpenHealthModal={() => setIsHealthModalOpen(true)}
          />

          <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
            <Routes>
              {/* Executive Overview */}
              <Route path="/" element={<DashboardPage />} />

              {/* MP Recommendation Portal */}
              <Route
                path="/recommendations"
                element={
                  <PlaceholderPage
                    title="MP Work Recommendation Portal"
                    moduleRole="Member 2 (Frontend Lead)"
                    phase="Phase 2 Sprint"
                    description="Allows Members of Parliament to submit developmental recommendations, select eligible categories under MPLADS guidelines, specify SC/ST mandate quotas, and receive instantaneous AI duplicate pre-check verification."
                    plannedFeatures={[
                      'Structured MP proposal submission wizard with coordinate picker',
                      'Automated 15% SC / 7.5% ST allocation tagging',
                      'Instant preliminary duplicate proposal check against nearby works',
                      'Constituency entitlement utilization dashboard',
                    ]}
                  />
                }
              />

              {/* District Collector Scrutiny Queue */}
              <Route
                path="/scrutiny"
                element={
                  <PlaceholderPage
                    title="District Collector Scrutiny & Sanction Portal"
                    moduleRole="Member 2 & Member 4"
                    phase="Phase 2 Sprint"
                    description="Provides District Magistrates and Collectors with an intelligent review inbox of proposed works. Highlights AI anomaly scores, estimated delay probability, and SOR cost variances before issuing Administrative & Financial Sanction (AS & FS)."
                    plannedFeatures={[
                      'Prioritized scrutiny queue sorted by AI risk score',
                      'Side-by-side SOR cost benchmark and Isolation Forest deviation',
                      'One-click Administrative & Financial Sanction workflow',
                      'Implementing Agency assignment based on historical efficiency ratings',
                    ]}
                  />
                }
              />

              {/* GIS Constituency Viewer */}
              <Route
                path="/gis-map"
                element={
                  <PlaceholderPage
                    title="Constituency GIS Map & Anti-Spoofing Viewer"
                    moduleRole="Member 3 (Frontend & GIS Specialist)"
                    phase="Phase 2 Sprint"
                    description="Interactive geospatial map rendering developmental works color-coded by lifecycle state. Visualizes the 300m radial duplicate detection boundary and validates field inspection coordinates."
                    plannedFeatures={[
                      'Interactive Leaflet / MapLibre basemaps with OpenStreetMap tiles',
                      'Constituency boundary polygon overlays with marker clustering',
                      'Anti-spoofing radial boundary validator for on-site inspection photos',
                      'Slide-out Project Dossier drawer on marker selection',
                    ]}
                  />
                }
              />

              {/* Fund Accounting & Quota Compliance */}
              <Route
                path="/funds"
                element={
                  <PlaceholderPage
                    title="Fund Allocation & Statutory Quota Tracker"
                    moduleRole="Member 4 & Member 5"
                    phase="Phase 3 Sprint"
                    description="Financial accounting engine monitoring the statutory ₹5.00 Crore annual entitlement per MP. Tracks tranche releases, ground utilization pacing, and enforces the mandatory 15% SC and 7.5% ST demographic allocations."
                    plannedFeatures={[
                      'Real-time statutory SC/ST quota compliance pacing gauge',
                      'Fiscal year-end fund lapse risk forecaster (90-day alert)',
                      'Bank account tranche disbursement tracking and expenditure ledger',
                      'State-wide and national inter-constituency equity benchmarks',
                    ]}
                  />
                }
              />

              {/* Citizen Transparency Portal */}
              <Route
                path="/citizen"
                element={
                  <PlaceholderPage
                    title="Public Citizen Transparency & Feedback Portal"
                    moduleRole="Member 3 (GIS & Public Portal)"
                    phase="Phase 4 Sprint"
                    description="Public-facing portal enabling citizens to search developmental projects by PIN code or Gram Panchayat, inspect verified before/after geotagged photos, and submit grievances or star ratings."
                    plannedFeatures={[
                      'Public search without requiring login (by PIN code or Constituency)',
                      'Printable & digital QR Code asset cards for on-site physical boards',
                      'Citizen feedback form with geo-verified photo attachment',
                      'Citizen grievance resolution status tracker',
                    ]}
                  />
                }
              />

              {/* System Diagnostics View */}
              <Route
                path="/diagnostics"
                element={
                  <PlaceholderPage
                    title="System Diagnostics & Gateway Status"
                    moduleRole="Member 1 (System Architect)"
                    phase="Phase 1 Active"
                    description="Real-time status monitor for FastAPI asynchronous gateway, PostgreSQL relational store, and sub-service communication channels."
                    plannedFeatures={[
                      'FastAPI /api/v1/health status and response latency telemetry',
                      'PostgreSQL connection pool and schema migration verification',
                      'CORS configuration validator and security header audit',
                      'Background worker and ML inference model readiness check',
                    ]}
                  />
                }
              />

              {/* Fallback redirect */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>

        {/* Gateway Diagnostics Modal */}
        <ApiStatusModal
          isOpen={isHealthModalOpen}
          onClose={() => setIsHealthModalOpen(false)}
          health={health}
          isLoading={isLoadingHealth}
          onRefresh={checkHealth}
        />
      </div>
    </BrowserRouter>
  );
};

export default App;
