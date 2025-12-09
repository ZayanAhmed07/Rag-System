import React from 'react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white border-t border-gray-200 px-6 py-4 text-center text-sm text-gray-600">
      <div className="flex justify-between items-center">
        <p>© {currentYear} RAG System. All rights reserved.</p>
        <div className="flex gap-6 text-xs">
          <a href="#" className="hover:text-gray-900 transition-colors">
            Documentation
          </a>
          <a href="#" className="hover:text-gray-900 transition-colors">
            API Docs
          </a>
          <a href="#" className="hover:text-gray-900 transition-colors">
            Support
          </a>
        </div>
      </div>
    </footer>
  );
}
