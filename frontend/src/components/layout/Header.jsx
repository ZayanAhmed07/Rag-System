import React from 'react';
import { Menu, X } from 'lucide-react';

export default function Header({ onMenuClick }) {
  const [dropdownOpen, setDropdownOpen] = React.useState(false);

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-40 shadow-sm">
      <div className="flex justify-between items-center">
        {/* Left Section */}
        <div className="flex items-center gap-4">
          <button
            onClick={onMenuClick}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Menu size={24} />
          </button>
          <h1 className="text-2xl font-bold text-gray-900">RAG System</h1>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-6">
          {/* Status Badge */}
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-600">System Operational</span>
          </div>

          {/* User Menu */}
          <div className="relative">
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                U
              </div>
              <span className="text-sm font-medium hidden sm:block">User</span>
            </button>

            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                <a href="#" className="block px-4 py-2 hover:bg-gray-100 text-sm">
                  Profile
                </a>
                <a href="#" className="block px-4 py-2 hover:bg-gray-100 text-sm">
                  Settings
                </a>
                <hr className="my-2" />
                <a href="#" className="block px-4 py-2 hover:bg-gray-100 text-sm text-red-600">
                  Logout
                </a>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
