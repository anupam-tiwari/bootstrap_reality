'use client';

import { useState } from 'react';
import { Brain, RotateCcw } from 'lucide-react';

export default function PieceDetector({ image, onPiecesDetected, onProcessingChange }) {
  const [detectedPieces, setDetectedPieces] = useState([]);
  const [isDetecting, setIsDetecting] = useState(false);

  const detectionMethod = 'hunyuan3d-2'; // We only use Tencent Hunyuan3D-2 now

  const detectPieces = async () => {
    setIsDetecting(true);
    onProcessingChange(true);

    try {
      const pieces = await generateWithHunyuan3D();
      setDetectedPieces(pieces);
      onPiecesDetected(pieces);
    } catch (error) {
      console.error('❌ 3D generation failed:', error);
      alert(`3D generation failed: ${error.message}`);
    } finally {
      setIsDetecting(false);
      onProcessingChange(false);
    }
  };

  const generateWithHunyuan3D = async () => {
    // Use Tencent Hunyuan3D-2 via backend Flask service
    const formData = new FormData();
    formData.append('image', image.file);
    
    console.log('🚀 Calling Tencent Hunyuan3D-2 API for 3D generation...');
    
    let response;
    try {
      response = await fetch('http://localhost:5051/api/3d-generation', {
        method: 'POST',
        body: formData
      });
    } catch (error) {
      console.error('❌ Network error:', error);
      throw new Error(`Failed to connect to backend server. Make sure the backend is running on port 5051: ${error.message}`);
    }
    
    console.log(`📡 API response status: ${response.status}`);
    
    const result = await response.json();
    console.log('📦 API result:', result);
    
    if (!response.ok) {
      throw new Error(`API error (${response.status}): ${result.error || result.message || 'Unknown error'}`);
    }
    
    if (!result.success) {
      throw new Error(result.error || result.message || 'API returned unsuccessful response');
    }
    
    if (!result.pieces || result.pieces.length === 0) {
      throw new Error('No 3D models generated');
    }
    
    console.log(`✅ Generated ${result.pieces.length} 3D models`);
    console.log('📦 Generated pieces:', result.pieces);
    result.pieces.forEach((piece, index) => {
      console.log(`📋 Piece ${index + 1}:`, {
        id: piece.id,
        name: piece.name,
        type: piece.type,
        assetUrl: piece.assetUrl,
        previewUrl: piece.previewUrl
      });
    });
    return result.pieces;
  };


  const resetDetection = () => {
    setDetectedPieces([]);
    onPiecesDetected([]);
  };

  return (
    <div className="space-y-4">
      {/* AI 3D Generation Method */}
      <div>
        <h3 className="text-lg font-medium text-gray-800 mb-3">AI 3D Generation</h3>
        <div className="flex items-center p-4 rounded-lg border-2 border-blue-500 bg-blue-50">
          <div className="text-blue-600 mr-3">
            <Brain className="h-5 w-5" />
          </div>
          <div className="flex-1">
            <div className="font-medium text-gray-800">Tencent Hunyuan3D-2</div>
            <div className="text-sm text-gray-600">Official AI model for high-quality 3D asset generation from images</div>
          </div>
        </div>
      </div>

      {/* Detection Controls */}
      <div className="flex gap-3">
        <button
          onClick={detectPieces}
          disabled={isDetecting}
          className={`
            flex-1 flex items-center justify-center px-4 py-2 rounded-lg font-medium transition-colors
            ${isDetecting 
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
              : 'bg-blue-600 text-white hover:bg-blue-700'
            }
          `}
        >
          {isDetecting ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Generating 3D Models...
            </>
          ) : (
            <>
              <Brain className="h-4 w-4 mr-2" />
              Generate 3D Models
            </>
          )}
        </button>
        
        {detectedPieces.length > 0 && (
          <button
            onClick={resetDetection}
            disabled={isDetecting}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* 3D Generation Results */}
      {detectedPieces.length > 0 && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center text-green-800 font-medium mb-2">
            <Brain className="h-4 w-4 mr-2" />
            3D Generation Complete!
          </div>
          <p className="text-sm text-green-700">
            Generated {detectedPieces.length} 3D model{detectedPieces.length !== 1 ? 's' : ''}. Check your library to view and interact with the 3D assets.
          </p>
        </div>
      )}
    </div>
  );
}
