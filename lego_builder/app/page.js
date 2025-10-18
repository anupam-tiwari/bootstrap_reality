'use client';

import { useState } from 'react';
import { Upload, Camera, Download, RotateCcw, Play, Pause } from 'lucide-react';
import ImageUpload from './components/ImageUpload';
import PieceDetector from './components/PieceDetector';
import AssetLibrary from './components/AssetLibrary';
import ThreeDViewer from './components/ThreeDViewer';

export default function Home() {
  const [uploadedImage, setUploadedImage] = useState(null);
  const [detectedPieces, setDetectedPieces] = useState([]);
  const [selectedPieces, setSelectedPieces] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleImageUpload = (image) => {
    setUploadedImage(image);
    setDetectedPieces([]);
    setSelectedPieces([]);
  };

  const handlePieceDetection = async (pieces) => {
    setDetectedPieces(pieces);
    setIsProcessing(false);
  };

  const handlePieceSelection = (piece) => {
    setSelectedPieces(prev => {
      const isSelected = prev.some(selected => selected.id === piece.id);
      if (isSelected) {
        return prev.filter(selected => selected.id !== piece.id);
      } else {
        return [...prev, piece];
      }
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            🧱 LEGO Builder AI
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Upload a photo of your LEGO set and watch as we convert each piece into a 3D asset 
            that you can play with in our virtual builder!
          </p>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Upload & Detection */}
          <div className="space-y-6">
            {/* Image Upload */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
                <Camera className="mr-2 text-blue-600" />
                Upload LEGO Set Photo
              </h2>
              <ImageUpload 
                onImageUpload={handleImageUpload}
                isProcessing={isProcessing}
              />
            </div>

            {/* Piece Detection */}
            {uploadedImage && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
                  <Upload className="mr-2 text-green-600" />
                  AI Piece Detection
                </h2>
                <PieceDetector 
                  image={uploadedImage}
                  onPiecesDetected={handlePieceDetection}
                  onProcessingChange={setIsProcessing}
                />
              </div>
            )}
          </div>

          {/* Right Column - 3D Viewer & Library */}
          <div className="space-y-6">
            {/* 3D Viewer */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
                <Play className="mr-2 text-purple-600" />
                3D Builder
              </h2>
              <ThreeDViewer 
                pieces={selectedPieces}
                onPieceSelect={handlePieceSelection}
              />
            </div>

            {/* Asset Library */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
                <Download className="mr-2 text-orange-600" />
                Your LEGO Library
              </h2>
              <AssetLibrary 
                pieces={detectedPieces}
                onPieceSelect={handlePieceSelection}
                selectedPieces={selectedPieces}
              />
            </div>
          </div>
        </div>

        {/* Processing Status */}
        {isProcessing && (
          <div className="fixed top-4 right-4 bg-blue-600 text-white px-6 py-3 rounded-lg shadow-lg flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-3"></div>
            AI is analyzing your LEGO set...
          </div>
        )}
      </div>
    </div>
  );
}
