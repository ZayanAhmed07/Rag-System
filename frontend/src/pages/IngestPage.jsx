import React, { useState } from 'react';
import { Card, Button, Badge, Alert, Spinner } from '../components/ui';
import { ingestService } from '../services/api';
import { Upload, Trash2, FileText, Check, AlertCircle } from 'lucide-react';

export default function IngestPage() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [uploading, setUploading] = useState({});

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;

    for (const file of files) {
      setUploading((prev) => ({ ...prev, [file.name]: true }));
      try {
        const response = await ingestService.uploadDocument(file, 'pdf');
        setDocuments((prev) => [response, ...prev]);
        setSuccess(`Successfully uploaded ${file.name}`);
        setTimeout(() => setSuccess(null), 3000);
      } catch (err) {
        setError(`Failed to upload ${file.name}: ${err.message}`);
        setTimeout(() => setError(null), 5000);
      } finally {
        setUploading((prev) => ({ ...prev, [file.name]: false }));
      }
    }
  };

  const handleDelete = async (docId) => {
    try {
      await ingestService.deleteDocument(docId);
      setDocuments((prev) => prev.filter((doc) => doc.id !== docId));
      setSuccess('Document deleted successfully');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(`Failed to delete document: ${err.message}`);
      setTimeout(() => setError(null), 5000);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Document Ingestion</h1>
        <p className="text-gray-600">Upload and manage documents for RAG system</p>
      </div>

      {/* Alerts */}
      {error && (
        <Alert variant="error" onClose={() => setError(null)}>
          <AlertCircle className="inline mr-2" size={18} />
          {error}
        </Alert>
      )}
      {success && (
        <Alert variant="success" onClose={() => setSuccess(null)}>
          <Check className="inline mr-2" size={18} />
          {success}
        </Alert>
      )}

      {/* Upload Card */}
      <Card className="border-2 border-dashed border-gray-300 hover:border-blue-500 transition-colors p-8">
        <label className="cursor-pointer flex flex-col items-center justify-center gap-4">
          <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center">
            <Upload className="text-blue-600" size={32} />
          </div>
          <div className="text-center">
            <p className="font-semibold text-lg">Drag and drop files here</p>
            <p className="text-sm text-gray-600">or click to select files</p>
          </div>
          <input
            type="file"
            multiple
            accept=".pdf,.docx,.txt"
            onChange={handleFileUpload}
            className="hidden"
            disabled={loading}
          />
        </label>
      </Card>

      {/* Documents List */}
      <Card>
        <h2 className="text-xl font-bold mb-4">Uploaded Documents</h2>
        {documents.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <FileText size={48} className="mx-auto mb-2 opacity-50" />
            <p>No documents uploaded yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
              >
                <div className="flex items-center gap-3 flex-1">
                  <FileText className="text-blue-600" size={24} />
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold truncate">{doc.filename}</p>
                    <p className="text-sm text-gray-500">
                      Uploaded {new Date(doc.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Badge variant="success">
                    {doc.chunks || 0} chunks
                  </Badge>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleDelete(doc.id)}
                    disabled={uploading[doc.filename]}
                  >
                    <Trash2 size={16} />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Statistics */}
      <Card className="bg-gradient-to-br from-blue-50 to-purple-50">
        <h2 className="text-xl font-bold mb-4">Ingestion Statistics</h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-3xl font-bold text-blue-600">{documents.length}</p>
            <p className="text-sm text-gray-600">Documents</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-green-600">
              {documents.reduce((sum, doc) => sum + (doc.chunks || 0), 0)}
            </p>
            <p className="text-sm text-gray-600">Total Chunks</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-purple-600">Ready</p>
            <p className="text-sm text-gray-600">Status</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
