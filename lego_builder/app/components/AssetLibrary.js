'use client';

import { useState } from 'react';
import { Plus, Download, Eye, Trash2, Search, Filter } from 'lucide-react';

export default function AssetLibrary({ pieces, onPieceSelect, selectedPieces }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [viewMode, setViewMode] = useState('grid');

  const filteredPieces = pieces.filter(piece => {
    const matchesSearch = piece.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         piece.type?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterType === 'all' || piece.type === filterType;
    return matchesSearch && matchesFilter;
  });

  const pieceTypes = [...new Set(pieces.map(piece => piece.type))];

  const handlePieceSelect = (piece) => {
    onPieceSelect(piece);
  };

  const handleDownload = (piece) => {
    // Download the 3D asset
    const link = document.createElement('a');
    link.href = piece.assetUrl;
    link.download = `${piece.name || '3d-model'}.glb`;
    link.click();
  };

  const isSelected = (piece) => {
    return selectedPieces.some(selected => selected.id === piece.id);
  };

  return (
    <div className="space-y-4">
      {/* Search and Filter Controls */}
      <div className="space-y-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search pieces..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        <div className="flex gap-2">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Types</option>
            {pieceTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
          
          <button
            onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
            className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Filter className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Pieces Grid/List */}
      {filteredPieces.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          {pieces.length === 0 ? (
            <div>
              <Download className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No pieces detected yet.</p>
              <p className="text-sm">Upload a LEGO set photo to get started!</p>
            </div>
          ) : (
            <div>
              <Search className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No pieces match your search.</p>
              <p className="text-sm">Try adjusting your search terms.</p>
            </div>
          )}
        </div>
      ) : (
        <div className={`
          ${viewMode === 'grid' 
            ? 'grid grid-cols-2 gap-3' 
            : 'space-y-3'
          }
        `}>
          {filteredPieces.map((piece) => (
            <div
              key={piece.id}
              className={`
                relative bg-white border-2 rounded-lg p-3 transition-all cursor-pointer
                ${isSelected(piece) 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
                }
                ${viewMode === 'list' ? 'flex items-center space-x-3' : ''}
              `}
              onClick={() => handlePieceSelect(piece)}
            >
              {/* Piece Preview */}
              <div className={`
                ${viewMode === 'grid' ? 'w-full h-24' : 'w-16 h-16'}
                bg-gray-100 rounded-lg flex items-center justify-center mb-2
                ${viewMode === 'list' ? 'mb-0' : ''}
              `}>
                {piece.previewUrl ? (
                  <img 
                    src={piece.previewUrl} 
                    alt={piece.name}
                    className="w-full h-full object-cover rounded-lg"
                  />
                ) : (
                  <div className="text-gray-400 text-2xl">🧱</div>
                )}
              </div>

              {/* Piece Info */}
              <div className={viewMode === 'list' ? 'flex-1' : ''}>
                <h4 className="font-medium text-gray-800 truncate">
                  {piece.name || `Piece ${piece.id}`}
                </h4>
                <p className="text-sm text-gray-600">
                  {piece.type || 'Unknown Type'}
                </p>
                {piece.dimensions && (
                  <p className="text-xs text-gray-500">
                    {piece.dimensions}
                  </p>
                )}
              </div>

              {/* Action Buttons */}
              <div className={`
                flex gap-1 mt-2
                ${viewMode === 'list' ? 'ml-auto' : ''}
              `}>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDownload(piece);
                  }}
                  className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                  title="Download 3D Asset"
                >
                  <Download className="h-4 w-4" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    // Preview piece in 3D viewer
                  }}
                  className="p-1 text-gray-400 hover:text-green-600 transition-colors"
                  title="Preview in 3D"
                >
                  <Eye className="h-4 w-4" />
                </button>
              </div>

              {/* Selection Indicator */}
              {isSelected(piece) && (
                <div className="absolute top-2 right-2 bg-blue-600 text-white rounded-full p-1">
                  <Plus className="h-3 w-3" />
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Selected Pieces Summary */}
      {selectedPieces.length > 0 && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-blue-800">
              {selectedPieces.length} piece{selectedPieces.length !== 1 ? 's' : ''} selected
            </span>
            <button
              onClick={() => {
                // Clear all selections
                selectedPieces.forEach(piece => {
                  // Remove from selected pieces
                });
              }}
              className="text-xs text-blue-600 hover:text-blue-800 transition-colors"
            >
              Clear All
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
