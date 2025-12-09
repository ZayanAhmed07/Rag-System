import React, { useState } from 'react';
import { Card, Button, Input, Badge, Spinner, Alert } from '../components/ui';
import { useQuery } from '../hooks';
import { Copy, Send, Loader } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function QueryPage() {
  const [queryText, setQueryText] = useState('');
  const [topK, setTopK] = useState(5);
  const [useCache, setUseCache] = useState(true);
  const [streamResponse, setStreamResponse] = useState('');
  const [streamSources, setStreamSources] = useState([]);
  const [streamStatus, setStreamStatus] = useState('');
  const [useStreaming, setUseStreaming] = useState(false);
  const { loading, error, data, query, streamQuery } = useQuery();

  const handleQuery = async (e) => {
    e.preventDefault();
    if (!queryText.trim()) return;

    if (useStreaming) {
      setStreamResponse('');
      setStreamSources([]);
      setStreamStatus('');
      try {
        await streamQuery(queryText, { top_k: topK, use_cache: useCache }, (event) => {
          if (event.type === 'status') {
            setStreamStatus(event.data.message);
          } else if (event.type === 'sources') {
            setStreamSources(event.data.sources);
          } else if (event.type === 'chunk') {
            setStreamResponse((prev) => prev + event.data.text);
          } else if (event.type === 'complete') {
            setStreamResponse(event.data.answer);
            setStreamStatus('Complete');
          }
        });
      } catch (err) {
        console.error('Streaming error:', err);
      }
    } else {
      try {
        await query(queryText, { top_k: topK, use_cache: useCache });
      } catch (err) {
        console.error('Query error:', err);
      }
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Query RAG System</h1>
        <p className="text-gray-600">Search through your documents with AI-powered retrieval</p>
      </div>

      {/* Query Form */}
      <Card>
        <form onSubmit={handleQuery} className="space-y-4">
          <div>
            <label className="label-base">Your Question</label>
            <textarea
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              placeholder="Ask anything about your documents..."
              className="input-base h-32 resize-none"
              disabled={loading}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              label="Top K Results"
              type="number"
              min="1"
              max="50"
              value={topK}
              onChange={(e) => setTopK(parseInt(e.target.value))}
            />
            <div className="flex items-end">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={useCache}
                  onChange={(e) => setUseCache(e.target.checked)}
                  className="w-4 h-4 accent-blue-600"
                />
                <span className="text-sm font-medium">Use Cache</span>
              </label>
            </div>
            <div className="flex items-end">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={useStreaming}
                  onChange={(e) => setUseStreaming(e.target.checked)}
                  className="w-4 h-4 accent-blue-600"
                />
                <span className="text-sm font-medium">Stream Response</span>
              </label>
            </div>
          </div>

          <Button
            type="submit"
            disabled={loading || !queryText.trim()}
            loading={loading}
            className="w-full"
          >
            <Send size={18} className="mr-2" />
            {loading ? 'Searching...' : 'Search Documents'}
          </Button>
        </form>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert variant="error" onClose={() => {}}>
          <strong>Error:</strong> {error}
        </Alert>
      )}

      {/* Streaming Status */}
      {useStreaming && streamStatus && (
        <Alert variant="info">
          <Loader className="inline animate-spin mr-2" size={16} />
          {streamStatus}
        </Alert>
      )}

      {/* Response Section */}
      {(data || streamResponse) && (
        <div className="space-y-4">
          {/* Generated Response */}
          <Card>
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-lg font-bold">Generated Response</h2>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => copyToClipboard(streamResponse || data?.response || '')}
              >
                <Copy size={16} />
              </Button>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 prose prose-sm max-w-none">
              {streamResponse ? (
                <ReactMarkdown>{streamResponse}</ReactMarkdown>
              ) : (
                <ReactMarkdown>{data?.response || ''}</ReactMarkdown>
              )}
            </div>
          </Card>

          {/* Retrieved Sources */}
          {((streamSources.length > 0) || (data?.sources && data.sources.length > 0)) && (
            <Card>
              <h2 className="text-lg font-bold mb-4">Retrieved Sources</h2>
              <div className="space-y-3">
                {(streamSources.length > 0 ? streamSources : data?.sources || []).map((source, idx) => (
                  <div
                    key={idx}
                    className="border border-gray-200 rounded-lg p-3 hover:shadow-md transition-shadow"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-semibold text-gray-900">
                        {source.document}
                        {source.index && <span className="text-blue-600 ml-2">[{source.index}]</span>}
                      </h3>
                      <Badge variant="success">{(source.score * 100).toFixed(1)}%</Badge>
                    </div>
                    <p className="text-gray-700 text-sm line-clamp-3">{source.content}</p>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Metadata */}
          {data?.metadata && (
            <Card className="bg-gray-50">
              <h2 className="text-lg font-bold mb-4">Query Metadata</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Retrieval Time</p>
                  <p className="font-semibold">{data.metadata.retrieval_time?.toFixed(2)}s</p>
                </div>
                <div>
                  <p className="text-gray-600">Generation Time</p>
                  <p className="font-semibold">{data.metadata.generation_time?.toFixed(2)}s</p>
                </div>
                <div>
                  <p className="text-gray-600">Cache Hit</p>
                  <Badge variant={data.metadata.cached ? 'success' : 'gray'}>
                    {data.metadata.cached ? 'Yes' : 'No'}
                  </Badge>
                </div>
              </div>
            </Card>
          )}
        </div>
      )}

      {/* Empty State */}
      {!data && !streamResponse && !loading && (
        <Card className="text-center py-12 bg-gradient-to-br from-blue-50 to-purple-50">
          <Send size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-600">Enter a query above to search your documents</p>
        </Card>
      )}
    </div>
  );
}
