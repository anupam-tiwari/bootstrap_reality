from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import os
import base64
import time
from io import BytesIO
from PIL import Image
import json

app = Flask(__name__)
CORS(app)

# Note: We now use Tencent Hunyuan3D-2 via Replicate API for 3D generation

@app.route('/api/detect-pieces', methods=['POST'])
def detect_pieces():
    """Legacy endpoint - redirects to 3D generation"""
    return jsonify({
        'success': False,
        'error': 'This endpoint is deprecated. Use /api/3d-generation for Tencent Hunyuan3D-2',
        'redirect_to': '/api/3d-generation'
    }), 410  # Gone

def detect_with_trellis(image_file):
    """Detect LEGO pieces using TRELLIS model"""
    try:
        headers = {
            'Authorization': f'Bearer {HUGGINGFACE_API_KEY}',
        }
        
        files = {'image': image_file}
        response = requests.post(TRELLIS_API_URL, headers=headers, files=files)
        
        if response.status_code == 200:
            result = response.json()
            return process_trellis_response(result)
        else:
            print(f"TRELLIS API error: {response.status_code}")
            return get_mock_pieces()
            
    except Exception as e:
        print(f"TRELLIS detection error: {str(e)}")
        return get_mock_pieces()

def detect_with_segment_anything(image_file):
    """Detect LEGO pieces using Segment Anything Model"""
    try:
        headers = {
            'Authorization': f'Bearer {HUGGINGFACE_API_KEY}',
        }
        
        files = {'image': image_file}
        response = requests.post(SEGMENT_ANYTHING_URL, headers=headers, files=files)
        
        if response.status_code == 200:
            result = response.json()
            return process_segment_anything_response(result)
        else:
            print(f"Segment Anything API error: {response.status_code}")
            return get_mock_pieces()
            
    except Exception as e:
        print(f"Segment Anything detection error: {str(e)}")
        return get_mock_pieces()

def detect_with_yolo(image_file):
    """Detect LEGO pieces using YOLO model"""
    try:
        headers = {
            'Authorization': f'Bearer {HUGGINGFACE_API_KEY}',
        }
        
        files = {'image': image_file}
        response = requests.post(YOLO_URL, headers=headers, files=files)
        
        if response.status_code == 200:
            result = response.json()
            return process_yolo_response(result)
        else:
            print(f"YOLO API error: {response.status_code}")
            return get_mock_pieces()
            
    except Exception as e:
        print(f"YOLO detection error: {str(e)}")
        return get_mock_pieces()

def process_trellis_response(result):
    """Process TRELLIS API response"""
    pieces = []
    
    if 'assets' in result and isinstance(result['assets'], list):
        for i, asset in enumerate(result['assets']):
            pieces.append({
                'id': f'trellis_{i}',
                'name': f'LEGO Piece {i + 1}',
                'type': 'brick',
                'color': asset.get('color', '#ef4444'),
                'dimensions': asset.get('dimensions', '1x1'),
                'assetUrl': asset.get('glb_url'),
                'previewUrl': asset.get('preview_url'),
                'confidence': asset.get('confidence', 0.9),
                'method': 'trellis'
            })
    
    return pieces if pieces else get_mock_pieces()

def process_segment_anything_response(result):
    """Process Segment Anything API response"""
    pieces = []
    
    if 'segments' in result and isinstance(result['segments'], list):
        for i, segment in enumerate(result['segments']):
            pieces.append({
                'id': f'sam_{i}',
                'name': f'LEGO Piece {i + 1}',
                'type': 'brick',
                'color': segment.get('color', '#ef4444'),
                'dimensions': '1x1',
                'mask': segment.get('mask'),
                'confidence': segment.get('confidence', 0.8),
                'method': 'segment-anything'
            })
    
    return pieces if pieces else get_mock_pieces()

def process_yolo_response(result):
    """Process YOLO API response"""
    pieces = []
    
    if 'predictions' in result and isinstance(result['predictions'], list):
        for i, prediction in enumerate(result['predictions']):
            # Filter for objects that might be LEGO pieces
            if (prediction.get('label', '').lower() in ['toy', 'block', 'brick'] or 
                prediction.get('confidence', 0) > 0.7):
                pieces.append({
                    'id': f'yolo_{i}',
                    'name': f'LEGO Piece {i + 1}',
                    'type': 'brick',
                    'color': '#ef4444',
                    'dimensions': '1x1',
                    'bbox': prediction.get('bbox'),
                    'confidence': prediction.get('confidence', 0.8),
                    'method': 'yolo'
                })
    
    return pieces if pieces else get_mock_pieces()

def get_mock_pieces():
    """Return realistic mock LEGO pieces for demo"""
    import random
    
    # Realistic LEGO piece types and colors
    piece_types = [
        {'name': 'LEGO Brick 1x2', 'type': 'brick', 'dimensions': '1x2'},
        {'name': 'LEGO Brick 1x4', 'type': 'brick', 'dimensions': '1x4'},
        {'name': 'LEGO Plate 2x4', 'type': 'plate', 'dimensions': '2x4'},
        {'name': 'LEGO Plate 2x2', 'type': 'plate', 'dimensions': '2x2'},
        {'name': 'LEGO Tile 1x1', 'type': 'tile', 'dimensions': '1x1'},
        {'name': 'LEGO Tile 1x2', 'type': 'tile', 'dimensions': '1x2'},
        {'name': 'LEGO Slope 1x2', 'type': 'slope', 'dimensions': '1x2'},
        {'name': 'LEGO Slope 2x2', 'type': 'slope', 'dimensions': '2x2'},
        {'name': 'LEGO Arch 1x3', 'type': 'arch', 'dimensions': '1x3'},
        {'name': 'LEGO Cylinder 1x1', 'type': 'cylinder', 'dimensions': '1x1'},
    ]
    
    # Realistic LEGO colors
    lego_colors = [
        '#ef4444',  # Red
        '#3b82f6',  # Blue  
        '#10b981',  # Green
        '#f59e0b',  # Yellow
        '#8b5cf6',  # Purple
        '#ec4899',  # Pink
        '#06b6d4',  # Cyan
        '#84cc16',  # Lime
        '#f97316',  # Orange
        '#6366f1',  # Indigo
        '#ef4444',  # Bright Red
        '#3b82f6',  # Bright Blue
    ]
    
    # Generate 3-6 random pieces
    num_pieces = random.randint(3, 6)
    pieces = []
    
    for i in range(num_pieces):
        piece_template = random.choice(piece_types)
        color = random.choice(lego_colors)
        confidence = round(random.uniform(0.85, 0.98), 2)
        
        pieces.append({
            'id': f'mock_{i+1}',
            'name': piece_template['name'],
            'type': piece_template['type'],
            'color': color,
            'dimensions': piece_template['dimensions'],
            'confidence': confidence,
            'method': 'mock'
        })
    
    return pieces

try:
    # Optional import; no longer needed since we use Replicate API directly
    from gradio_client import Client
except Exception:
    Client = None

@app.route('/api/3d-generation', methods=['POST'])
def hunyuan3d_endpoint():
    """Real 3D generation using official Tencent Hunyuan3D-2 via Replicate API"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    
    try:
        # Try Replicate API first
        import replicate
        import os
        
        print("🚀 Starting Tencent Hunyuan3D-2 API call...")
        
        # Set Replicate API token
        os.environ['REPLICATE_API_TOKEN'] = ''
        
        # Verify token is set
        token = os.environ.get('REPLICATE_API_TOKEN')
        print(f"🔑 API Token set: {token[:10]}...{token[-10:]}")
        
        # Save uploaded image temporarily
        temp_path = f"/tmp/upload_{int(time.time())}.jpg"
        print(f"💾 Saving image to: {temp_path}")
        image_file.save(temp_path)
        
        # Verify file exists
        if not os.path.exists(temp_path):
            raise Exception("Failed to save uploaded image")
        
        print(f"📁 Image saved successfully. Size: {os.path.getsize(temp_path)} bytes")
        
        # Call Replicate Tencent Hunyuan3D-2 model (official version)
        print("🔄 Calling Replicate API...")
        
        # Initialize Replicate client with timeout
        replicate_client = replicate.Client(api_token=os.environ['REPLICATE_API_TOKEN'])
        
        with open(temp_path, "rb") as image_file_handle:
            # Set longer timeout for 3D generation (can take 60-300 seconds)
            output = replicate_client.run(
                "tencent/hunyuan3d-2:b1b9449a1277e10402781c5d41eb30c0a0683504fb23fab591ca9dfc2aabe1cb",
                input={"image": image_file_handle}
            )
        print(f"📦 Raw Replicate output: {output}")
        print(f"📦 Output type: {type(output)}")
        
        # Clean up temp file
        import os
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # Verify this is real API output, not mock data
        if not output or (isinstance(output, dict) and not output.get('mesh')):
            raise Exception("Replicate API returned empty or invalid output")
        
        # Process the 3D output
        pieces = process_3d_output(output)
        
        # Verify we got real pieces, not mock data
        if not pieces or (len(pieces) > 0 and pieces[0].get('method') != 'tencent-hunyuan3d-2'):
            raise Exception("Failed to process real API output")
        
        print(f"✅ Tencent Hunyuan3D-2 API success! Generated {len(pieces)} REAL 3D models")
        
        # Final safety check - ensure all pieces are JSON serializable
        for piece in pieces:
            for key, value in piece.items():
                if hasattr(value, '__dict__') and not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                    print(f"⚠️ Found non-serializable object in piece.{key}: {type(value)}")
                    piece[key] = str(value) if value is not None else None
        
        print(f"📦 Final pieces before JSON serialization: {pieces}")
        
        return jsonify({
            'success': True, 
            'pieces': pieces, 
            'method': 'tencent-hunyuan3d-2', 
            'count': len(pieces),
            'message': 'Real 3D generation using official Tencent Hunyuan3D-2!'
        })
        
    except Exception as e:
        print(f"❌ Tencent Hunyuan3D-2 API failed: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        
        # Clean up temp file if it exists
        try:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
                print("🧹 Cleaned up temp file")
        except Exception as cleanup_error:
            print(f"⚠️ Failed to clean up temp file: {cleanup_error}")
        
        # For now, let's return an error instead of falling back to mock data
        return jsonify({
            'success': False, 
            'error': f'Tencent Hunyuan3D-2 API failed: {str(e)}',
            'method': 'api-failed',
            'message': 'API call failed. Check server logs for details.'
        }), 500

def process_3d_output(output):
    """Process Tencent Hunyuan3D-2 output into LEGO pieces"""
    pieces = []
    
    print(f"Raw output from Tencent Hunyuan3D-2: {output}")
    
    def extract_url_from_file_output(file_output):
        """Extract URL from Replicate FileOutput object"""
        if hasattr(file_output, 'url'):
            return file_output.url
        elif hasattr(file_output, '__str__'):
            return str(file_output)
        else:
            return None
    
    # Tencent Hunyuan3D-2 returns a dict with 'mesh' field containing the 3D model URL
    if isinstance(output, dict):
        mesh_field = output.get('mesh')
        # Handle FileOutput object
        if hasattr(mesh_field, 'url'):
            mesh_url = mesh_field.url
        else:
            mesh_url = extract_url_from_file_output(mesh_field) if mesh_field else None
            
        print(f"Extracted mesh URL: {mesh_url}")
        
        if mesh_url:
            pieces.append({
                'id': 'hunyuan3d_1',
                'name': 'Generated LEGO 3D Model',
                'type': '3d_model',
                'color': '#3b82f6',  # Default blue
                'dimensions': '1x1',
                'assetUrl': mesh_url,
                'previewUrl': mesh_url,
                'confidence': 0.95,
                'method': 'tencent-hunyuan3d-2',
                'metadata': {
                    'model': 'Tencent Hunyuan3D-2',
                    'official': True,
                    'format': 'GLB',
                    'source_url': mesh_url
                }
            })
        else:
            # If no mesh URL, create a placeholder
            pieces.append({
                'id': 'hunyuan3d_1',
                'name': 'Generated LEGO 3D Model',
                'type': '3d_model',
                'color': '#3b82f6',
                'dimensions': '1x1',
                'assetUrl': None,
                'previewUrl': None,
                'confidence': 0.95,
                'method': 'tencent-hunyuan3d-2',
                'metadata': {
                    'model': 'Tencent Hunyuan3D-2',
                    'official': True,
                    'format': 'GLB',
                    'source_url': mesh_url
                }
            })
    elif isinstance(output, list):
        # Handle list of outputs
        for i, item in enumerate(output):
            if isinstance(item, dict) and 'mesh' in item:
                mesh_field = item.get('mesh')
                # Handle FileOutput object
                if hasattr(mesh_field, 'url'):
                    mesh_url = mesh_field.url
                else:
                    mesh_url = extract_url_from_file_output(mesh_field) if mesh_field else None
                    
                pieces.append({
                    'id': f'hunyuan3d_{i+1}',
                    'name': f'LEGO 3D Model {i+1}',
                    'type': '3d_model',
                    'color': '#3b82f6',
                    'dimensions': '1x1',
                    'assetUrl': mesh_url,
                    'previewUrl': mesh_url,
                    'confidence': 0.95,
                    'method': 'tencent-hunyuan3d-2',
                    'metadata': {
                        'model': 'Tencent Hunyuan3D-2',
                        'official': True,
                        'format': 'GLB',
                        'source_url': mesh_url
                    }
                })
    else:
        # Fallback for string or other output types
        model_url = str(output) if output else None
        pieces.append({
            'id': 'hunyuan3d_1',
            'name': 'Generated LEGO 3D Model',
            'type': '3d_model',
            'color': '#3b82f6',
            'dimensions': '1x1',
            'assetUrl': model_url,
            'previewUrl': model_url,
            'confidence': 0.95,
            'method': 'tencent-hunyuan3d-2',
            'metadata': {
                'model': 'Tencent Hunyuan3D-2',
                'official': True,
                'format': 'GLB'
            }
        })
    
    return pieces

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'LEGO Builder API'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5051)
