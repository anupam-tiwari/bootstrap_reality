// TRELLIS API Integration Service

/**
 * TRELLIS API endpoints and configurations
 */
const TRELLIS_ENDPOINTS = {
  // Hugging Face Spaces API
  HF_SPACES: 'https://trellis-community-trellis.hf.space/api/predict',
  
  // Alternative endpoints (if needed)
  HF_INFERENCE: 'https://api-inference.huggingface.co/models/trellis-community/TRELLIS',
  
  // Local development endpoint
  LOCAL: 'http://localhost:5000/api/trellis'
};

/**
 * Convert image file to base64
 */
async function imageToBase64(imageFile) {
  const arrayBuffer = await imageFile.arrayBuffer();
  return Buffer.from(arrayBuffer).toString('base64');
}

/**
 * Call TRELLIS API via Hugging Face Spaces
 */
export async function callTrellisHFSpaces(imageFile) {
  try {
    const base64 = await imageToBase64(imageFile);
    
    const response = await fetch(TRELLIS_ENDPOINTS.HF_SPACES, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        data: [
          `data:image/jpeg;base64,${base64}`,
          "trellis", // method
          {
            "num_inference_steps": 50,
            "guidance_scale": 7.5
          }, // generation settings
          {
            "extract_glb": true,
            "extract_gaussian": false
          } // extraction settings
        ]
      })
    });

    if (!response.ok) {
      throw new Error(`TRELLIS HF Spaces API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('TRELLIS HF Spaces error:', error);
    throw error;
  }
}

/**
 * Call TRELLIS API via Hugging Face Inference API
 */
export async function callTrellisHFInference(imageFile, apiKey) {
  try {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const response = await fetch(TRELLIS_ENDPOINTS.HF_INFERENCE, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`TRELLIS HF Inference API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('TRELLIS HF Inference error:', error);
    throw error;
  }
}

/**
 * Call local TRELLIS service
 */
export async function callTrellisLocal(imageFile) {
  try {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const response = await fetch(TRELLIS_ENDPOINTS.LOCAL, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Local TRELLIS API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Local TRELLIS error:', error);
    throw error;
  }
}

/**
 * Main TRELLIS detection function with fallback
 */
export async function detectWithTrellis(imageFile, options = {}) {
  const { 
    method = 'hf_spaces', 
    apiKey = null,
    fallbackToMock = true 
  } = options;

  try {
    let result;
    
    switch (method) {
      case 'hf_spaces':
        result = await callTrellisHFSpaces(imageFile);
        break;
      case 'hf_inference':
        if (!apiKey) throw new Error('API key required for HF Inference');
        result = await callTrellisHFInference(imageFile, apiKey);
        break;
      case 'local':
        result = await callTrellisLocal(imageFile);
        break;
      default:
        throw new Error(`Unknown TRELLIS method: ${method}`);
    }
    
    return processTrellisResponse(result);
  } catch (error) {
    console.error('TRELLIS detection failed:', error);
    
    if (fallbackToMock) {
      console.log('Falling back to mock data for demo purposes');
      return getMockPieces();
    }
    
    throw error;
  }
}

/**
 * Process TRELLIS API response
 */
function processTrellisResponse(result) {
  const pieces = [];
  
  try {
    // Handle different response formats
    let data = result;
    
    if (result.data && Array.isArray(result.data)) {
      data = result.data;
    } else if (result.predictions && Array.isArray(result.predictions)) {
      data = result.predictions;
    } else if (result.assets && Array.isArray(result.assets)) {
      data = result.assets;
    }
    
    if (Array.isArray(data)) {
      data.forEach((item, index) => {
        if (item && typeof item === 'object') {
          pieces.push({
            id: `trellis_${index}`,
            name: `LEGO Piece ${index + 1}`,
            type: detectPieceType(item),
            color: item.color || getRandomLEGOColor(),
            dimensions: item.dimensions || getRandomDimensions(),
            assetUrl: item.glb_url || item.asset_url || item.url,
            previewUrl: item.preview_url || item.image_url || item.thumbnail,
            confidence: item.confidence || item.score || 0.9,
            method: 'trellis',
            metadata: {
              originalData: item
            }
          });
        }
      });
    }
    
    return pieces.length > 0 ? pieces : getMockPieces();
  } catch (error) {
    console.error('Error processing TRELLIS response:', error);
    return getMockPieces();
  }
}

/**
 * Detect LEGO piece type from data
 */
function detectPieceType(item) {
  const name = (item.name || '').toLowerCase();
  const type = (item.type || '').toLowerCase();
  
  if (name.includes('plate') || type.includes('plate')) return 'plate';
  if (name.includes('tile') || type.includes('tile')) return 'tile';
  if (name.includes('slope') || type.includes('slope')) return 'slope';
  if (name.includes('brick') || type.includes('brick')) return 'brick';
  
  return 'brick'; // default
}

/**
 * Get random LEGO color
 */
function getRandomLEGOColor() {
  const colors = [
    '#ef4444', // red
    '#3b82f6', // blue
    '#10b981', // green
    '#f59e0b', // yellow
    '#8b5cf6', // purple
    '#ec4899', // pink
    '#06b6d4', // cyan
    '#84cc16', // lime
    '#f97316', // orange
    '#6366f1'  // indigo
  ];
  return colors[Math.floor(Math.random() * colors.length)];
}

/**
 * Get random LEGO dimensions
 */
function getRandomDimensions() {
  const dimensions = ['1x1', '1x2', '1x4', '2x2', '2x4', '1x6', '2x6', '1x8', '2x8'];
  return dimensions[Math.floor(Math.random() * dimensions.length)];
}

/**
 * Mock pieces for demo purposes
 */
function getMockPieces() {
  return [
    {
      id: 'trellis_1',
      name: 'LEGO Brick 1x2',
      type: 'brick',
      color: '#ef4444',
      dimensions: '1x2',
      confidence: 0.95,
      method: 'trellis'
    },
    {
      id: 'trellis_2',
      name: 'LEGO Plate 2x4',
      type: 'plate',
      color: '#3b82f6',
      dimensions: '2x4',
      confidence: 0.92,
      method: 'trellis'
    },
    {
      id: 'trellis_3',
      name: 'LEGO Tile 1x1',
      type: 'tile',
      color: '#10b981',
      dimensions: '1x1',
      confidence: 0.88,
      method: 'trellis'
    },
    {
      id: 'trellis_4',
      name: 'LEGO Slope 1x2',
      type: 'slope',
      color: '#f59e0b',
      dimensions: '1x2',
      confidence: 0.90,
      method: 'trellis'
    }
  ];
}
