import React, { useState, useEffect } from 'react';
import { Card, Button, Input, Badge } from '../components/ui';
import { evaluationService } from '../services/api';
import { BarChart3, TrendingUp } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function EvaluationPage() {
  const [metrics, setMetrics] = useState(null);
  const [evaluationResults, setEvaluationResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    queryText: '',
    response: '',
    groundTruth: '',
  });

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const data = await evaluationService.getMetrics();
      setMetrics(data);
    } catch (err) {
      console.error('Failed to fetch metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluate = async (e) => {
    e.preventDefault();
    try {
      const result = await evaluationService.evaluate(
        formData.queryText,
        formData.response,
        formData.groundTruth
      );
      setEvaluationResults((prev) => [result, ...prev]);
      setFormData({ queryText: '', response: '', groundTruth: '' });
    } catch (err) {
      console.error('Evaluation failed:', err);
    }
  };

  const chartData = metrics?.history || [];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">RAG Evaluation</h1>
        <p className="text-gray-600">Monitor and evaluate RAG system performance</p>
      </div>

      {/* Key Metrics */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            { label: 'Avg Relevance', value: metrics.avg_relevance?.toFixed(2), color: 'blue' },
            { label: 'Answer Relevance', value: metrics.answer_relevance?.toFixed(2), color: 'green' },
            { label: 'Context Recall', value: metrics.context_recall?.toFixed(2), color: 'purple' },
            { label: 'Context Precision', value: metrics.context_precision?.toFixed(2), color: 'orange' },
          ].map((metric, idx) => (
            <Card key={idx} className={`bg-${metric.color}-50 border-l-4 border-${metric.color}-500`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{metric.label}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{metric.value}</p>
                </div>
                <TrendingUp className={`text-${metric.color}-600`} size={32} />
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Performance Chart */}
      {chartData.length > 0 && (
        <Card>
          <h2 className="text-lg font-bold mb-4">Performance Trends</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="relevance" stroke="#3B82F6" />
              <Line type="monotone" dataKey="answer_relevance" stroke="#10B981" />
              <Line type="monotone" dataKey="context_recall" stroke="#8B5CF6" />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      )}

      {/* Evaluation Form */}
      <Card>
        <h2 className="text-lg font-bold mb-4">Evaluate Response</h2>
        <form onSubmit={handleEvaluate} className="space-y-4">
          <div>
            <label className="label-base">Query</label>
            <textarea
              value={formData.queryText}
              onChange={(e) => setFormData({ ...formData, queryText: e.target.value })}
              placeholder="Enter the query..."
              className="input-base h-24 resize-none"
            />
          </div>

          <div>
            <label className="label-base">Generated Response</label>
            <textarea
              value={formData.response}
              onChange={(e) => setFormData({ ...formData, response: e.target.value })}
              placeholder="Enter the generated response..."
              className="input-base h-24 resize-none"
            />
          </div>

          <div>
            <label className="label-base">Ground Truth (Expected Answer)</label>
            <textarea
              value={formData.groundTruth}
              onChange={(e) => setFormData({ ...formData, groundTruth: e.target.value })}
              placeholder="Enter the expected answer..."
              className="input-base h-24 resize-none"
            />
          </div>

          <Button type="submit" className="w-full" variant="primary">
            Evaluate Response
          </Button>
        </form>
      </Card>

      {/* Results */}
      {evaluationResults.length > 0 && (
        <Card>
          <h2 className="text-lg font-bold mb-4">Evaluation Results</h2>
          <div className="space-y-4">
            {evaluationResults.map((result, idx) => (
              <div key={idx} className="border border-gray-200 rounded-lg p-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Relevance</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {(result.relevance_score * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Answer Relevance</p>
                    <p className="text-2xl font-bold text-green-600">
                      {(result.answer_relevance * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Context Recall</p>
                    <p className="text-2xl font-bold text-purple-600">
                      {(result.context_recall * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Context Precision</p>
                    <p className="text-2xl font-bold text-orange-600">
                      {(result.context_precision * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
