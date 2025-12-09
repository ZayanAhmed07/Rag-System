import React from 'react';
import { Zap, Database, Layout as LayoutIcon } from 'lucide-react';

/**
 * FRONTEND ARCHITECTURE OVERVIEW
 * 
 * This document provides a visual overview of the component relationships
 * and the microservices-like architecture pattern used in this project.
 */

export default function ArchitectureGuide() {
  return (
    <div className="space-y-8 p-8">
      {/* Title */}
      <div>
        <h1 className="text-4xl font-bold mb-2">Frontend Architecture</h1>
        <p className="text-gray-600">Component-Based Design with Microservices Pattern</p>
      </div>

      {/* Diagram 1: Component Hierarchy */}
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <LayoutIcon size={24} />
          Component Hierarchy
        </h2>
        <div className="bg-gray-100 rounded-lg p-6 overflow-x-auto">
          <pre className="text-sm font-mono">{`
App (Router)
├── Header (Navigation)
├── Sidebar (Menu)
├── Main Content Area
│   ├── QueryPage
│   │   └── QueryForm + ResultsDisplay
│   ├── IngestPage
│   │   └── UploadZone + DocumentsList
│   ├── EvaluationPage
│   │   └── MetricsChart + EvaluationForm
│   └── SettingsPage
│       └── SettingsForm + SystemInfo
└── Footer (Links)
          `}</pre>
        </div>
      </section>

      {/* Diagram 2: Data Flow */}
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Zap size={24} />
          Data Flow (Microservices Style)
        </h2>
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="bg-white rounded-lg p-4 min-w-fit shadow">Page Component</div>
              <div className="flex-1 h-px bg-gray-300"></div>
              <div className="bg-white rounded-lg p-4 min-w-fit shadow">Custom Hook</div>
            </div>
            <div className="flex items-center gap-4">
              <div className="bg-white rounded-lg p-4 min-w-fit shadow">Custom Hook</div>
              <div className="flex-1 h-px bg-gray-300"></div>
              <div className="bg-white rounded-lg p-4 min-w-fit shadow">Service Layer</div>
            </div>
            <div className="flex items-center gap-4">
              <div className="bg-white rounded-lg p-4 min-w-fit shadow">Service Layer</div>
              <div className="flex-1 h-px bg-gray-300"></div>
              <div className="bg-white rounded-lg p-4 min-w-fit shadow">Backend API</div>
            </div>
          </div>
        </div>
      </section>

      {/* Services Breakdown */}
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Database size={24} />
          Service Layer (Microservices)
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            {
              name: 'queryService',
              methods: ['query(text, options)', 'streamQuery(text, options)', 'getStats()'],
            },
            {
              name: 'ingestService',
              methods: ['uploadDocument(file)', 'getDocuments()', 'deleteDocument(id)', 'searchDocuments(query)'],
            },
            {
              name: 'evaluationService',
              methods: ['evaluate(...)', 'getEvaluationResults()', 'getMetrics()'],
            },
            {
              name: 'settingsService',
              methods: ['getSettings()', 'updateSettings()', 'getSystemInfo()'],
            },
          ].map((service) => (
            <div key={service.name} className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
              <h3 className="font-bold text-lg mb-2">{service.name}</h3>
              <ul className="space-y-1 text-sm">
                {service.methods.map((method, idx) => (
                  <li key={idx} className="text-gray-700">• {method}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* Custom Hooks */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Custom Hooks (State Management)</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            {
              name: 'useQuery',
              returns: '{ loading, error, data, query, streamQuery }',
              use: 'Manage query state and API calls',
            },
            {
              name: 'useAsync',
              returns: '{ execute, status, value, error }',
              use: 'Generic async operation handling',
            },
            {
              name: 'useLocalStorage',
              returns: '[storedValue, setValue]',
              use: 'Persist data in browser storage',
            },
            {
              name: 'useDebounce',
              returns: 'debouncedValue',
              use: 'Optimize frequent state changes',
            },
          ].map((hook) => (
            <div key={hook.name} className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
              <h3 className="font-bold text-lg mb-2">{hook.name}</h3>
              <p className="text-sm text-gray-600 mb-2"><strong>Returns:</strong> {hook.returns}</p>
              <p className="text-sm text-gray-700"><strong>Use:</strong> {hook.use}</p>
            </div>
          ))}
        </div>
      </section>

      {/* UI Components */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Atomic UI Components</h2>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              'Button',
              'Card',
              'Input',
              'Select',
              'Modal',
              'Toast',
              'Badge',
              'Spinner',
              'Alert',
            ].map((component) => (
              <div key={component} className="border border-gray-200 rounded-lg p-3 text-center text-sm font-medium">
                {component}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Design Principles */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Design Principles</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            {
              principle: 'Separation of Concerns',
              description: 'Services, hooks, and components have distinct responsibilities',
            },
            {
              principle: 'Reusability',
              description: 'Components can be composed and combined in multiple ways',
            },
            {
              principle: 'Maintainability',
              description: 'Clear structure makes it easy to find and update code',
            },
            {
              principle: 'Testability',
              description: 'Independent modules are easier to unit test',
            },
            {
              principle: 'Scalability',
              description: 'Services can be easily extended or replaced',
            },
            {
              principle: 'Single Responsibility',
              description: 'Each component/hook does one thing well',
            },
          ].map((item) => (
            <div key={item.principle} className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
              <h3 className="font-bold text-blue-900 mb-1">{item.principle}</h3>
              <p className="text-sm text-blue-800">{item.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Technology Stack */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Technology Stack</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { category: 'Framework', tech: 'React 18.2 + Vite' },
            { category: 'Routing', tech: 'React Router v6' },
            { category: 'Styling', tech: 'Tailwind CSS + PostCSS' },
            { category: 'API Client', tech: 'Axios' },
            { category: 'Icons', tech: 'Lucide React' },
            { category: 'Charts', tech: 'Recharts' },
          ].map((item) => (
            <div key={item.category} className="bg-white rounded-lg shadow p-4">
              <p className="text-sm text-gray-600">{item.category}</p>
              <p className="font-bold text-lg">{item.tech}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
