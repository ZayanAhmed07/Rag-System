import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import Footer from './components/layout/Footer';
import QueryPage from './pages/QueryPage';
import IngestPage from './pages/IngestPage';
import EvaluationPage from './pages/EvaluationPage';
import SettingsPage from './pages/SettingsPage';
import './styles/globals.css';

export default function App() {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  return (
    <Router>
      <div className="flex h-screen bg-gray-50">
        {/* Sidebar */}
        <Sidebar isOpen={sidebarOpen} />

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

          {/* Page Content */}
          <main className="flex-1 overflow-auto">
            <div className="p-6">
              <Routes>
                <Route path="/" element={<QueryPage />} />
                <Route path="/ingest" element={<IngestPage />} />
                <Route path="/evaluation" element={<EvaluationPage />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Routes>
            </div>
          </main>

          {/* Footer */}
          <Footer />
        </div>
      </div>
    </Router>
  );
}
