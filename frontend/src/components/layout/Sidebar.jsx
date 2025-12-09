import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Search, Upload, BarChart3, Settings, ChevronDown } from 'lucide-react';

const menuItems = [
  { path: '/', label: 'Query', icon: Search },
  { path: '/ingest', label: 'Ingest', icon: Upload },
  { path: '/evaluation', label: 'Evaluation', icon: BarChart3 },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar({ isOpen }) {
  const location = useLocation();

  return (
    <aside
      className={`bg-gray-900 text-white transition-all duration-300 ${
        isOpen ? 'w-64' : 'w-20'
      } border-r border-gray-800 flex flex-col overflow-hidden`}
    >
      {/* Logo */}
      <div className="p-6 flex items-center gap-3 border-b border-gray-800">
        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center font-bold text-xl">
          R
        </div>
        {isOpen && <span className="font-bold text-lg">RAG</span>}
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
              title={!isOpen ? item.label : ''}
            >
              <Icon size={20} className="flex-shrink-0" />
              {isOpen && <span className="font-medium">{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Footer Info */}
      {isOpen && (
        <div className="p-4 border-t border-gray-800 space-y-3">
          <div className="text-xs text-gray-400">
            <p className="font-semibold mb-1">System Status</p>
            <p className="flex items-center gap-2">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              Connected
            </p>
          </div>
        </div>
      )}
    </aside>
  );
}
