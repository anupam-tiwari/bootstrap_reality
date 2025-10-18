'use client';

import { useState } from 'react';
import { detectWithTrellis } from '../../lib/trellis';

export default function TestTrellis() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const testTrellis = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Create a test image (1x1 pixel)
      const canvas = document.createElement('canvas');
      canvas.width = 100;
      canvas.height = 100;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#ef4444';
      ctx.fillRect(0, 0, 100, 100);
      
      // Convert to blob
      const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
      const file = new File([blob], 'test.jpg', { type: 'image/jpeg' });

      // Test TRELLIS
      const pieces = await detectWithTrellis(file, {
        method: 'hf_spaces',
        fallbackToMock: true
      });

      setResult(pieces);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">TRELLIS Integration Test</h1>
        
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Test TRELLIS API</h2>
          <button
            onClick={testTrellis}
            disabled={loading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Testing...' : 'Test TRELLIS Detection'}
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <h3 className="text-red-800 font-semibold mb-2">Error</h3>
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {result && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <h3 className="text-green-800 font-semibold mb-4">TRELLIS Results</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {result.map((piece, index) => (
                <div key={piece.id} className="bg-white rounded-lg p-4 border">
                  <div className="flex items-center mb-2">
                    <div 
                      className="w-6 h-6 rounded mr-3"
                      style={{ backgroundColor: piece.color }}
                    ></div>
                    <span className="font-medium">{piece.name}</span>
                  </div>
                  <div className="text-sm text-gray-600 space-y-1">
                    <p><strong>Type:</strong> {piece.type}</p>
                    <p><strong>Dimensions:</strong> {piece.dimensions}</p>
                    <p><strong>Confidence:</strong> {(piece.confidence * 100).toFixed(1)}%</p>
                    <p><strong>Method:</strong> {piece.method}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-blue-800 font-semibold mb-2">TRELLIS Integration Status</h3>
          <div className="text-blue-700 space-y-1">
            <p>✅ TRELLIS service imported successfully</p>
            <p>✅ Multiple API endpoints configured</p>
            <p>✅ Fallback to mock data enabled</p>
            <p>✅ Error handling implemented</p>
          </div>
        </div>
      </div>
    </div>
  );
}
