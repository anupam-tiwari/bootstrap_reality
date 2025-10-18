'use client';

import { useState, useEffect } from 'react';
import { RotateCcw, ZoomIn, ZoomOut, Play, Pause, Move, RotateCw } from 'lucide-react';

// Simple 3D LEGO Piece Component with drag and drop support
function LegoPiece({ piece, index, onSelect, isSelected, isRotating, position, onDragEnd }) {
  const [isHovered, setIsHovered] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const handleClick = () => {
    onSelect(piece);
  };

  const handleDragStart = (e) => {
    setIsDragging(true);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', JSON.stringify({ pieceId: piece.id, index }));
  };

  const handleDragEnd = (e) => {
    setIsDragging(false);
    if (onDragEnd) {
      onDragEnd(e, piece);
    }
  };

  const pieceStyle = {
    backgroundColor: piece.color || '#ef4444',
    transform: isRotating ? `rotateY(${Date.now() * 0.001}rad)` : 'none',
    transition: 'all 0.3s ease',
    transformStyle: 'preserve-3d',
    cursor: 'pointer',
    border: isSelected ? '3px solid #3b82f6' : isHovered ? '2px solid #10b981' : '1px solid #d1d5db',
    boxShadow: isHovered ? '0 8px 25px rgba(0,0,0,0.15)' : '0 4px 12px rgba(0,0,0,0.1)',
    transform: isHovered ? 'scale(1.05) translateY(-2px)' : 'scale(1)',
  };

  return (
    <div
      className="relative group"
      style={{
        perspective: '1000px',
        transform: position ? `translate(${position.x}%, ${position.y}%)` : `translateZ(${index * 10}px)`,
        position: position ? 'absolute' : 'relative',
        zIndex: isDragging ? 1000 : 1,
        cursor: isDragging ? 'grabbing' : 'grab',
      }}
      draggable
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div
        className="lego-piece"
        style={{
          ...pieceStyle,
          opacity: isDragging ? 0.7 : 1,
        }}
        onClick={handleClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* LEGO studs on top */}
        <div className="absolute inset-0 flex flex-wrap justify-center items-center p-1">
          {Array.from({ length: 4 }).map((_, i) => (
            <div
              key={i}
              className="w-1 h-1 bg-white rounded-full opacity-60"
              style={{
                margin: '1px',
                boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.3)'
              }}
            />
          ))}
        </div>
        
        {/* Piece label */}
        <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-xs p-1 text-center opacity-0 group-hover:opacity-100 transition-opacity">
          {piece.name || `Piece ${index + 1}`}
        </div>
      </div>
    </div>
  );
}

// Main 3D Viewer Component
export default function ThreeDViewer({ pieces, onPieceSelect }) {
  const [selectedPieces, setSelectedPieces] = useState([]);
  const [isRotating, setIsRotating] = useState(true);
  const [zoom, setZoom] = useState(1);
  const [viewMode, setViewMode] = useState('grid'); // grid, list, isometric
  const [positionedPieces, setPositionedPieces] = useState({}); // Track piece positions for drag & drop

  const handlePieceSelect = (piece) => {
    const isSelected = selectedPieces.some(selected => selected.id === piece.id);
    if (isSelected) {
      setSelectedPieces(prev => prev.filter(selected => selected.id !== piece.id));
    } else {
      setSelectedPieces(prev => [...prev, piece]);
    }
    onPieceSelect(piece);
  };

  const toggleRotation = () => {
    setIsRotating(!isRotating);
  };

  const adjustZoom = (direction) => {
    setZoom(prev => {
      const newZoom = direction === 'in' ? prev * 1.2 : prev / 1.2;
      return Math.max(0.5, Math.min(3, newZoom));
    });
  };

  const cycleViewMode = () => {
    const modes = ['grid', 'list', 'isometric'];
    const currentIndex = modes.indexOf(viewMode);
    setViewMode(modes[(currentIndex + 1) % modes.length]);
  };

  // Drag and drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e) => {
    e.preventDefault();
    try {
      const dragData = JSON.parse(e.dataTransfer.getData('text/plain'));
      const { pieceId } = dragData;
      
      const piece = pieces.find(p => p.id === pieceId);
      if (piece) {
        const rect = e.currentTarget.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        
        setPositionedPieces(prev => ({
          ...prev,
          [pieceId]: { x, y }
        }));
        
        // Auto-select the dropped piece
        if (!selectedPieces.some(selected => selected.id === pieceId)) {
          handlePieceSelect(piece);
        }
      }
    } catch (error) {
      console.error('Drag and drop error:', error);
    }
  };

  const handlePieceDragEnd = (e, piece) => {
    // This is handled by the drop event above
  };

  const resetView = () => {
    setSelectedPieces([]);
    setZoom(1);
    setPositionedPieces({});
  };

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          <button
            onClick={toggleRotation}
            className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            title={isRotating ? 'Pause rotation' : 'Start rotation'}
          >
            {isRotating ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </button>
          <button
            onClick={resetView}
            className="p-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            title="Reset view"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
          <button
            onClick={cycleViewMode}
            className="p-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            title="Change view mode"
          >
            <Move className="h-4 w-4" />
          </button>
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={() => adjustZoom('out')}
            className="p-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            title="Zoom out"
          >
            <ZoomOut className="h-4 w-4" />
          </button>
          <span className="px-2 py-1 text-sm text-gray-600 bg-gray-100 rounded">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={() => adjustZoom('in')}
            className="p-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            title="Zoom in"
          >
            <ZoomIn className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* 3D Scene */}
      <div 
        className="w-full h-96 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg overflow-hidden relative"
        style={{
          transform: `scale(${zoom})`,
          transformOrigin: 'center',
        }}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        {pieces.length === 0 ? (
          <div className="w-full h-full flex items-center justify-center text-gray-500">
            <div className="text-center">
              <div className="text-6xl mb-4">🧱</div>
              <p className="text-lg font-medium">No pieces to display</p>
              <p className="text-sm">Select pieces from your library to start building!</p>
            </div>
          </div>
        ) : (
          <>
            {/* Grid Layout for non-positioned pieces */}
            <div 
              className={`w-full h-full p-4 ${
                viewMode === 'grid' 
                  ? 'grid grid-cols-3 gap-4' 
                  : viewMode === 'list'
                  ? 'flex flex-col gap-2'
                  : 'flex flex-wrap gap-4 justify-center items-center'
              }`}
              style={{
                perspective: viewMode === 'isometric' ? '1000px' : 'none',
                transform: viewMode === 'isometric' ? 'rotateX(15deg) rotateY(-15deg)' : 'none',
              }}
            >
              {pieces
                .filter(piece => !positionedPieces[piece.id])
                .map((piece, index) => (
                  <LegoPiece
                    key={piece.id}
                    piece={piece}
                    index={index}
                    onSelect={handlePieceSelect}
                    isSelected={selectedPieces.some(selected => selected.id === piece.id)}
                    isRotating={isRotating}
                    position={null}
                    onDragEnd={handlePieceDragEnd}
                  />
                ))}
            </div>
            
            {/* Positioned pieces for drag & drop */}
            {pieces
              .filter(piece => positionedPieces[piece.id])
              .map((piece, index) => (
                <LegoPiece
                  key={`positioned-${piece.id}`}
                  piece={piece}
                  index={index}
                  onSelect={handlePieceSelect}
                  isSelected={selectedPieces.some(selected => selected.id === piece.id)}
                  isRotating={isRotating}
                  position={positionedPieces[piece.id]}
                  onDragEnd={handlePieceDragEnd}
                />
              ))}
          </>
        )}

        {/* Ground plane effect */}
        <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-gray-200 to-transparent opacity-30"></div>
      </div>

      {/* Piece Info */}
      {selectedPieces.length > 0 && (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="font-medium text-blue-800 mb-2">
            Selected Pieces ({selectedPieces.length})
          </h4>
          <div className="space-y-1">
            {selectedPieces.map(piece => (
              <div key={piece.id} className="text-sm text-blue-700 flex items-center justify-between">
                <span>• {piece.name || `Piece ${piece.id}`} - {piece.type || 'Unknown Type'}</span>
                <span className="text-xs bg-blue-200 px-2 py-1 rounded">
                  {piece.dimensions || '1x1'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* View Mode Indicator */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <div>
          Mode: <span className="font-medium capitalize">{viewMode}</span>
        </div>
        <div className="space-y-1">
          <p>• Click pieces to select them</p>
          <p>• Drag pieces from library to position them</p>
          <p>• Use controls to rotate, zoom, and change view</p>
        </div>
      </div>
    </div>
  );
}
