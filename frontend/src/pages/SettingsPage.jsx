import React, { useState, useEffect } from 'react';
import { Card, Button, Input, Badge } from '../components/ui';
import { settingsService } from '../services/api';
import { Settings as SettingsIcon, Save, RotateCcw } from 'lucide-react';

export default function SettingsPage() {
  const [settings, setSettings] = useState(null);
  const [systemInfo, setSystemInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const [settingsData, infoData] = await Promise.all([
        settingsService.getSettings(),
        settingsService.getSystemInfo(),
      ]);
      setSettings(settingsData);
      setSystemInfo(infoData);
    } catch (err) {
      console.error('Failed to fetch settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      await settingsService.updateSettings(settings);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error('Failed to save settings:', err);
    }
  };

  const handleReset = () => {
    fetchSettings();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-gray-600">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-gray-600">Configure RAG system parameters and preferences</p>
      </div>

      {/* System Information */}
      {systemInfo && (
        <Card>
          <h2 className="text-lg font-bold mb-4">System Information</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Version</p>
              <p className="font-semibold">{systemInfo.version}</p>
            </div>
            <div>
              <p className="text-gray-600">Environment</p>
              <Badge>{systemInfo.environment}</Badge>
            </div>
            <div>
              <p className="text-gray-600">Uptime</p>
              <p className="font-semibold">{systemInfo.uptime}</p>
            </div>
            <div>
              <p className="text-gray-600">Database</p>
              <Badge variant="success">Connected</Badge>
            </div>
            <div>
              <p className="text-gray-600">Vector Store</p>
              <Badge variant="success">Connected</Badge>
            </div>
            <div>
              <p className="text-gray-600">Cache</p>
              <Badge variant="success">Connected</Badge>
            </div>
          </div>
        </Card>
      )}

      {/* RAG Settings */}
      {settings && (
        <Card>
          <h2 className="text-lg font-bold mb-4">RAG Configuration</h2>
          <div className="space-y-4">
            <Input
              label="Model Name"
              value={settings.model_name || ''}
              onChange={(e) =>
                setSettings({ ...settings, model_name: e.target.value })
              }
            />

            <Input
              label="Top K Results"
              type="number"
              value={settings.top_k || 5}
              onChange={(e) =>
                setSettings({ ...settings, top_k: parseInt(e.target.value) })
              }
            />

            <Input
              label="Similarity Threshold"
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={settings.similarity_threshold || 0.5}
              onChange={(e) =>
                setSettings({ ...settings, similarity_threshold: parseFloat(e.target.value) })
              }
            />

            <div>
              <label className="label-base">Temperature</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={settings.temperature || 0.7}
                onChange={(e) =>
                  setSettings({ ...settings, temperature: parseFloat(e.target.value) })
                }
                className="w-full"
              />
              <p className="text-sm text-gray-600 mt-1">
                Current: {settings.temperature || 0.7}
              </p>
            </div>

            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={settings.enable_caching || false}
                  onChange={(e) =>
                    setSettings({ ...settings, enable_caching: e.target.checked })
                  }
                  className="w-4 h-4 accent-blue-600"
                />
                <span className="font-medium">Enable Response Caching</span>
              </label>

              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={settings.enable_monitoring || false}
                  onChange={(e) =>
                    setSettings({ ...settings, enable_monitoring: e.target.checked })
                  }
                  className="w-4 h-4 accent-blue-600"
                />
                <span className="font-medium">Enable Performance Monitoring</span>
              </label>

              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={settings.enable_logging || false}
                  onChange={(e) =>
                    setSettings({ ...settings, enable_logging: e.target.checked })
                  }
                  className="w-4 h-4 accent-blue-600"
                />
                <span className="font-medium">Enable Detailed Logging</span>
              </label>
            </div>
          </div>
        </Card>
      )}

      {/* Save Status */}
      {saved && (
        <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg">
          ✓ Settings saved successfully!
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3 justify-end">
        <Button variant="secondary" onClick={handleReset}>
          <RotateCcw size={18} className="mr-2" />
          Reset
        </Button>
        <Button variant="primary" onClick={handleSave}>
          <Save size={18} className="mr-2" />
          Save Changes
        </Button>
      </div>

      {/* Advanced Settings */}
      <Card className="border-2 border-dashed border-gray-300">
        <h2 className="text-lg font-bold mb-4">Advanced Settings</h2>
        <p className="text-gray-600 mb-4">
          For more advanced configuration, please edit the backend config.py file or use environment variables.
        </p>
        <ul className="space-y-2 text-sm text-gray-700">
          <li>• <code className="bg-gray-100 px-2 py-1 rounded">HUGGINGFACE_API_KEY</code> - HuggingFace authentication</li>
          <li>• <code className="bg-gray-100 px-2 py-1 rounded">QDRANT_URL</code> - Vector database endpoint</li>
          <li>• <code className="bg-gray-100 px-2 py-1 rounded">DATABASE_URL</code> - PostgreSQL connection</li>
          <li>• <code className="bg-gray-100 px-2 py-1 rounded">REDIS_URL</code> - Cache database</li>
        </ul>
      </Card>
    </div>
  );
}
