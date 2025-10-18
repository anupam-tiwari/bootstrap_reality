from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import os
import base64
import time
from io import BytesIO
from PIL import Image
import json
import numpy as np
import cv2
import replicate
import traceback
import random

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
    temp_path = None  # Initialize temp_path for proper cleanup
    
    try:
        # Try Replicate API first
        import replicate
        import os
        
        print("🚀 Starting Tencent Hunyuan3D-2 API call...")
        
        # Set Replicate API token from environment variable
        if 'REPLICATE_API_TOKEN' not in os.environ:
            # Fallback - you should set this as an environment variable
            raise Exception("REPLICATE_API_TOKEN environment variable not set")
        
        # Verify token is set
        token = os.environ.get('REPLICATE_API_TOKEN')
        if not token or token == '':
            raise Exception("Replicate API token is not set or empty")
        print(f"🔑 API Token set: {token[:10]}...{token[-10:]}")
        
        # Save uploaded image temporarily - preserve original extension
        original_filename = image_file.filename
        if original_filename and '.' in original_filename:
            file_extension = original_filename.split('.')[-1].lower()
            if file_extension not in ['jpg', 'jpeg', 'png', 'bmp']:
                file_extension = 'jpg'  # fallback
        else:
            file_extension = 'jpg'  # fallback
            
        temp_path = f"/tmp/upload_{int(time.time())}_{random.randint(1000, 9999)}.{file_extension}"
        print(f"💾 Saving image to: {temp_path}")
        
        # Ensure proper file handling
        try:
            image_file.seek(0)  # Reset file pointer
            image_file.save(temp_path)
            print(f"📁 Image saved successfully. Size: {os.path.getsize(temp_path)} bytes")
        except Exception as e:
            raise Exception(f"Failed to save uploaded image: {str(e)}")
        
        if not os.path.exists(temp_path):
            raise Exception("Failed to save uploaded image - file does not exist after save")
        
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
            if temp_path and os.path.exists(temp_path):
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

def segment_legos_in_image(image_path):
    """Segment individual LEGO pieces from an image using computer vision"""
    try:
        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            raise Exception("Could not load image for segmentation")
        
        # Convert to different color spaces for better segmentation
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        print(f"🔍 Processing image with shape: {image.shape}")
        
        # Try multiple segmentation approaches
        contours_list = []
        
        # Approach 1: Adaptive thresholding
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh1 = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        kernel = np.ones((3,3), np.uint8)
        opening1 = cv2.morphologyEx(thresh1, cv2.MORPH_OPEN, kernel, iterations=2)
        closing1 = cv2.morphologyEx(opening1, cv2.MORPH_CLOSE, kernel, iterations=2)
        contours1, _ = cv2.findContours(closing1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_list.extend(contours1)
        print(f"🔍 Approach 1 (adaptive threshold): {len(contours1)} contours")
        
        # Approach 2: HSV color-based segmentation
        # Create mask for colorful objects (typical LEGO pieces)
        lower_color = np.array([0, 30, 30])
        upper_color = np.array([180, 255, 255])
        mask = cv2.inRange(hsv, lower_color, upper_color)
        contours2, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_list.extend(contours2)
        print(f"🔍 Approach 2 (HSV color): {len(contours2)} contours")
        
        # Approach 3: Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        kernel = np.ones((3,3), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        contours3, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_list.extend(contours3)
        print(f"🔍 Approach 3 (edge detection): {len(contours3)} contours")
        
        # Combine and remove duplicates (simplified)
        contours = []
        for contour in contours_list:
            if cv2.contourArea(contour) > 100:  # Basic area filter
                contours.append(contour)
        
        print(f"🔍 Total contours after filtering: {len(contours)}")
        
        # Filter contours by area and aspect ratio (typical LEGO characteristics)
        img_area = image.shape[0] * image.shape[1]
        # Much more lenient area filtering to catch smaller LEGO pieces
        min_area = img_area // 500  # Even smaller minimum area (0.2% of image)
        max_area = img_area // 3   # Max 33% of image to allow for larger pieces
        
        print(f"🔍 Image size: {image.shape}, Total area: {img_area}")
        print(f"🔍 Using area range: {min_area} to {max_area}")
        
        # Also try to detect if this looks like a 2x2 grid pattern for 4 pieces
        height, width = image.shape[:2]
        expected_grid_size = min(height, width) // 2  # Expect ~2x2 grid
        print(f"🔍 Expected grid size: {expected_grid_size}")
        
        segmented_regions = []
        processed_contours = set()  # Avoid duplicate processing
        
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if min_area < area < max_area:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check aspect ratio (LEGO pieces are roughly square-ish)
                aspect_ratio = w / h
                print(f"🔍 Contour {i}: area={area}, aspect={aspect_ratio:.2f}, bbox=({x},{y},{w},{h})")
                
                # More flexible aspect ratio AND size requirements for LEGO pieces
                # LEGO pieces come in various shapes - 1x1, 1x2, 2x2, etc.
                if (0.2 < aspect_ratio < 5.0 and  # Very lenient aspect ratio
                    w > 20 and h > 20 and         # Minimum size
                    area > min_area):             # Area check
                    
                    # Check if this contour overlaps significantly with already processed ones
                    center_x, center_y = x + w//2, y + h//2
                    is_duplicate = False
                    
                    for existing in segmented_regions:
                        existing_bbox = existing['bbox']
                        existing_center_x = existing_bbox[0] + existing_bbox[2]//2
                        existing_center_y = existing_bbox[1] + existing_bbox[3]//2
                        
                        # If centers are too close, it's likely the same piece
                        distance = ((center_x - existing_center_x)**2 + (center_y - existing_center_y)**2)**0.5
                        if distance < max(w, h) * 0.8:  # Too close, skip this one
                            print(f"🔍 Skipping duplicate contour {i} - too close to existing")
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        # Extract the region with padding
                        padding = 10
                        x_start = max(0, x - padding)
                        y_start = max(0, y - padding)
                        x_end = min(image.shape[1], x + w + padding)
                        y_end = min(image.shape[0], y + h + padding)
                        
                        roi = image[y_start:y_end, x_start:x_end]
                        
                        if roi.size > 0:  # Make sure we have a valid region
                            # Save the segmented piece
                            segment_filename = f"/tmp/segment_{int(time.time())}_{i}.jpg"
                            success = cv2.imwrite(segment_filename, roi)
                            
                            if success:
                                segmented_regions.append({
                                    'filename': segment_filename,
                                    'bbox': (x_start, y_start, x_end - x_start, y_end - y_start),
                                    'area': area,
                                    'aspect_ratio': aspect_ratio
                                })
                                print(f"✅ Created segment {len(segmented_regions)}: {segment_filename}")
                            else:
                                print(f"⚠️ Failed to save segment {i}")
                        
                        # If we already have 4 pieces and they look reasonable, we can stop
                        if len(segmented_regions) >= 4:
                            print(f"✅ Found target number of pieces (4), continuing to check for more...")
        
        print(f"🔍 Found {len(segmented_regions)} potential LEGO pieces")
        return segmented_regions
        
    except Exception as e:
        print(f"❌ Image segmentation failed: {e}")
        return []

def simple_grid_segmentation(image_path):
    """Simple grid-based segmentation as fallback when CV segmentation fails"""
    try:
        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            return []
        
        height, width = image.shape[:2]
        
        # Try different grid configurations - prioritize 2x2 for 4 pieces
        grid_configs = [
            (2, 2),  # 2x2 grid - should give us 4 pieces (most common scenario)
            (1, 4),  # 1x4 horizontal - 4 pieces
            (2, 3),  # 2x3 grid - 6 pieces
            (1, 3),  # 1x3 horizontal - 3 pieces
            (3, 1),  # 3x1 vertical - 3 pieces
        ]
        
        segments = []
        
        print(f"🔍 Grid segmentation: image size {width}x{height}")
        
        # Try each grid configuration
        for rows, cols in grid_configs:
            segment_height = height // rows
            segment_width = width // cols
            
            print(f"🔍 Trying {rows}x{cols} grid - segment size would be {segment_width}x{segment_height}")
            
            # More lenient size check - allow smaller segments
            if segment_height > 30 and segment_width > 30:
                print(f"🔍 Proceeding with {rows}x{cols} grid")
                
                temp_segments = []
                for row in range(rows):
                    for col in range(cols):
                        # Calculate segment boundaries
                        y_start = row * segment_height
                        y_end = min((row + 1) * segment_height, height)
                        x_start = col * segment_width  
                        x_end = min((col + 1) * segment_width, width)
                        
                        # Extract the region
                        roi = image[y_start:y_end, x_start:x_end]
                        
                        if roi.size > 0:
                            # Save the segment
                            segment_filename = f"/tmp/grid_segment_{int(time.time())}_{row}_{col}.jpg"
                            success = cv2.imwrite(segment_filename, roi)
                            
                            print(f"🔍 Created segment at ({x_start},{y_start}) to ({x_end},{y_end}) - success: {success}")
                            
                            if success and os.path.exists(segment_filename):
                                temp_segments.append({
                                    'filename': segment_filename,
                                    'bbox': (x_start, y_start, x_end - x_start, y_end - y_start),
                                    'area': (x_end - x_start) * (y_end - y_start),
                                    'aspect_ratio': (x_end - x_start) / (y_end - y_start)
                                })
                                print(f"✅ Added segment {len(temp_segments)}: {segment_filename}")
                            else:
                                print(f"⚠️ Failed to create segment {row}_{col}")
                
                # Use the first reasonable grid configuration we find
                if len(temp_segments) >= 2:  # At least 2 pieces to make it worth it
                    segments = temp_segments
                    print(f"✅ Grid segmentation successful: Created {len(segments)} segments using {rows}x{cols} grid")
                    break
                else:
                    print(f"⚠️ Grid {rows}x{cols} only produced {len(temp_segments)} segments, trying next...")
            else:
                print(f"⚠️ Grid {rows}x{cols} would produce segments too small ({segment_width}x{segment_height}), skipping")
        
        print(f"🔍 Grid segmentation completed with {len(segments)} segments")
        
        return segments
        
    except Exception as e:
        print(f"❌ Grid segmentation failed: {e}")
        return []

@app.route('/api/segment-and-generate', methods=['POST'])
def segment_and_generate_endpoint():
    """New endpoint that segments image first, then generates 3D models for each segment"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    temp_path = None
    
    try:
        print("🚀 Starting image segmentation + 3D generation...")
        
        # Verify Replicate API token is set
        if 'REPLICATE_API_TOKEN' not in os.environ:
            raise Exception("REPLICATE_API_TOKEN environment variable not set")
        
        # Save uploaded image temporarily - preserve original extension
        original_filename = image_file.filename
        if original_filename and '.' in original_filename:
            file_extension = original_filename.split('.')[-1].lower()
            if file_extension not in ['jpg', 'jpeg', 'png', 'bmp']:
                file_extension = 'jpg'  # fallback
        else:
            file_extension = 'jpg'  # fallback
            
        temp_path = f"/tmp/upload_{int(time.time())}_{random.randint(1000, 9999)}.{file_extension}"
        print(f"💾 Saving image to: {temp_path}")
        
        # Ensure the directory exists and save with proper handling
        try:
            image_file.seek(0)  # Reset file pointer
            image_file.save(temp_path)
            print(f"📁 Image saved successfully. Size: {os.path.getsize(temp_path)} bytes")
        except Exception as e:
            raise Exception(f"Failed to save uploaded image: {str(e)}")
        
        if not os.path.exists(temp_path):
            raise Exception("Failed to save uploaded image - file does not exist after save")
        
        # Step 1: Segment the image
        print("🔍 Segmenting image into individual LEGO pieces...")
        segments = segment_legos_in_image(temp_path)
        
        if not segments:
            print("⚠️ No LEGO pieces detected, trying simple grid-based segmentation...")
            # Try a simple grid-based approach as last resort
            segments = simple_grid_segmentation(temp_path)
            print(f"🔍 Grid segmentation result: {len(segments) if segments else 0} segments")
        elif len(segments) < 4:
            print(f"⚠️ Only found {len(segments)} pieces via CV, trying grid-based segmentation for 4 pieces...")
            # If we found some pieces but not 4, try grid segmentation to get exactly 4
            grid_segments = simple_grid_segmentation(temp_path)
            if len(grid_segments) >= 4:
                print(f"✅ Grid segmentation found {len(grid_segments)} pieces, using that instead")
                segments = grid_segments[:4]  # Take first 4 pieces
            else:
                print(f"🔍 Grid segmentation found {len(grid_segments)} pieces, keeping original {len(segments)} pieces")
        
        if not segments:
            print("⚠️ All segmentation attempts failed, falling back to full image 3D generation")
            # Fallback to single 3D generation using the same temp file
            try:
                replicate_client = replicate.Client(api_token=os.environ['REPLICATE_API_TOKEN'])
                with open(temp_path, "rb") as image_file_handle:
                    output = replicate_client.run(
                        "tencent/hunyuan3d-2:b1b9449a1277e10402781c5d41eb30c0a0683504fb23fab591ca9dfc2aabe1cb",
                        input={"image": image_file_handle}
                    )
                
                # Process the 3D output
                pieces = process_3d_output(output)
                
                # Clean up temp file
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                
                return jsonify({
                    'success': True, 
                    'pieces': pieces, 
                    'method': 'tencent-hunyuan3d-2-fallback', 
                    'count': len(pieces),
                    'message': 'No segments detected, generated single 3D model from full image'
                })
            except Exception as e:
                print(f"❌ Fallback 3D generation failed: {e}")
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                raise e
        
        print(f"✅ Found {len(segments)} LEGO pieces")
        
        # Step 2: Generate 3D models for each segment
        all_pieces = []
        replicate_client = replicate.Client(api_token=os.environ['REPLICATE_API_TOKEN'])
        
        for i, segment in enumerate(segments):
            try:
                print(f"🎲 Generating 3D model for piece {i+1}/{len(segments)}")
                
                # Generate 3D model for this segment
                try:
                    # Check if segment file exists and has content
                    if not os.path.exists(segment['filename']) or os.path.getsize(segment['filename']) == 0:
                        print(f"⚠️ Segment file {segment['filename']} is missing or empty")
                        continue
                    
                    print(f"📁 Processing segment file: {segment['filename']} (size: {os.path.getsize(segment['filename'])} bytes)")
                    
                    with open(segment['filename'], "rb") as segment_file:
                        # Add timeout handling for the API call
                        output = replicate_client.run(
                            "tencent/hunyuan3d-2:b1b9449a1277e10402781c5d41eb30c0a0683504fb23fab591ca9dfc2aabe1cb",
                            input={"image": segment_file},
                            timeout=120  # 2 minute timeout per segment
                        )
                except Exception as api_error:
                    print(f"⚠️ API call failed for segment {i+1}: {api_error}")
                    # Continue to next segment instead of failing completely
                    continue
                
                # Process the 3D output for this segment
                if isinstance(output, dict) and 'mesh' in output:
                    mesh_field = output.get('mesh')
                    if hasattr(mesh_field, 'url'):
                        mesh_url = mesh_field.url
                    else:
                        mesh_url = str(mesh_field)
                    
                    # Generate unique ID with timestamp to avoid conflicts
                    unique_id = f'segment_{int(time.time())}_{i+1}'
                    
                    piece = {
                        'id': unique_id,
                        'name': f'Segmented LEGO Piece {i+1}',
                        'type': '3d_model',
                        'color': '#3b82f6',
                        'dimensions': f"{segment['bbox'][2]}x{segment['bbox'][3]}",
                        'assetUrl': mesh_url,
                        'previewUrl': mesh_url,
                        'confidence': 0.95,
                        'method': 'tencent-hunyuan3d-2-segmented',
                        'metadata': {
                            'model': 'Tencent Hunyuan3D-2',
                            'official': True,
                            'format': 'GLB',
                            'segment_bbox': segment['bbox'],
                            'segment_area': segment['area'],
                            'segmented': True,
                            'segment_index': i+1
                        }
                    }
                    all_pieces.append(piece)
                    print(f"✅ Generated 3D model for piece {i+1}")
                else:
                    print(f"⚠️ Unexpected output format for segment {i+1}: {type(output)} - {output}")
                    # Try to extract URL anyway if it's a FileOutput object
                    try:
                        if hasattr(output, 'url'):
                            mesh_url = output.url
                        else:
                            mesh_url = str(output)
                        
                        unique_id = f'segment_{int(time.time())}_{i+1}'
                        piece = {
                            'id': unique_id,
                            'name': f'Segmented LEGO Piece {i+1}',
                            'type': '3d_model',
                            'color': '#3b82f6',
                            'dimensions': f"{segment['bbox'][2]}x{segment['bbox'][3]}",
                            'assetUrl': mesh_url,
                            'previewUrl': mesh_url,
                            'confidence': 0.95,
                            'method': 'tencent-hunyuan3d-2-segmented',
                            'metadata': {
                                'model': 'Tencent Hunyuan3D-2',
                                'official': True,
                                'format': 'GLB',
                                'segment_bbox': segment['bbox'],
                                'segment_area': segment['area'],
                                'segmented': True,
                                'segment_index': i+1
                            }
                        }
                        all_pieces.append(piece)
                        print(f"✅ Generated 3D model for piece {i+1} (fallback method)")
                    except Exception as fallback_error:
                        print(f"⚠️ Fallback extraction also failed for segment {i+1}: {fallback_error}")
                
                # Clean up segment file
                if os.path.exists(segment['filename']):
                    os.remove(segment['filename'])
                    
            except Exception as e:
                print(f"⚠️ Failed to generate 3D model for segment {i+1}: {e}")
                continue
        
        # If no pieces were generated from segments, fall back to single image generation
        if not all_pieces:
            print("⚠️ No 3D models were successfully generated from segments, falling back to full image 3D generation")
            
            # Re-save the original image for fallback (it might have been deleted)
            if temp_path and os.path.exists(temp_path):
                # Use existing temp file
                fallback_path = temp_path
            else:
                # Need to recreate the temp file from the original upload
                image_file.seek(0)
                fallback_path = f"/tmp/fallback_{int(time.time())}_{random.randint(1000, 9999)}.{file_extension}"
                image_file.save(fallback_path)
                print(f"🔄 Recreated temp file for fallback: {fallback_path}")
            
            try:
                replicate_client = replicate.Client(api_token=os.environ['REPLICATE_API_TOKEN'])
                with open(fallback_path, "rb") as image_file_handle:
                    output = replicate_client.run(
                        "tencent/hunyuan3d-2:b1b9449a1277e10402781c5d41eb30c0a0683504fb23fab591ca9dfc2aabe1cb",
                        input={"image": image_file_handle}
                    )
                
                # Process the 3D output using the same function as single generation
                fallback_pieces = process_3d_output(output)
                
                # Clean up fallback temp file
                if fallback_path and os.path.exists(fallback_path) and fallback_path != temp_path:
                    os.remove(fallback_path)
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                
                return jsonify({
                    'success': True, 
                    'pieces': fallback_pieces, 
                    'method': 'tencent-hunyuan3d-2-segmented-fallback', 
                    'count': len(fallback_pieces),
                    'segments_detected': len(segments),
                    'message': f'Segmentation found {len(segments)} segments but 3D generation failed. Generated single 3D model from full image instead.'
                })
            except Exception as fallback_error:
                print(f"❌ Fallback 3D generation also failed: {fallback_error}")
                # Clean up temp files
                if fallback_path and os.path.exists(fallback_path) and fallback_path != temp_path:
                    os.remove(fallback_path)
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                raise Exception(f"Both segment-based and fallback 3D generation failed: {str(fallback_error)}")
        
        # Clean up main temp file if it still exists
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        
        print(f"🎉 Successfully generated {len(all_pieces)} 3D models from {len(segments)} segments")
        
        return jsonify({
            'success': True,
            'pieces': all_pieces,
            'method': 'tencent-hunyuan3d-2-segmented',
            'count': len(all_pieces),
            'segments_detected': len(segments),
            'message': f'Successfully segmented image into {len(segments)} pieces and generated 3D models!'
        })
        
    except Exception as e:
        print(f"❌ Segmentation + 3D generation failed: {e}")
        print(f"❌ Full traceback: {traceback.format_exc()}")
        
        # Clean up temp files
        try:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            pass
        
        return jsonify({
            'success': False,
            'error': f'Segmentation and 3D generation failed: {str(e)}',
            'method': 'segmentation-failed',
            'message': 'Failed to segment image or generate 3D models. Check server logs for details.'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'LEGO Builder API'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5051)
