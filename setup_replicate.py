#!/usr/bin/env python3
"""
Setup script for Replicate API integration
"""

import os
import sys

def setup_replicate():
    print("🚀 Setting up Replicate API with Hunyuan3D-2 for LEGO Builder...")
    print()
    
    print("1. Go to https://replicate.com")
    print("2. Sign up for a free account")
    print("3. Go to your account settings")
    print("4. Copy your API token")
    print("5. Model: Hunyuan3D-2 (optimized for 3D generation)")
    print()
    
    token = input("Enter your Replicate API token: ").strip()
    
    if not token:
        print("❌ No token provided. Exiting.")
        return
    
    # Update the server.py file
    server_file = "backend/server.py"
    
    try:
        with open(server_file, 'r') as f:
            content = f.read()
        
        # Replace the placeholder token
        updated_content = content.replace(
            "os.environ['REPLICATE_API_TOKEN'] = 'your_replicate_token_here'",
            f"os.environ['REPLICATE_API_TOKEN'] = '{token}'"
        )
        
        with open(server_file, 'w') as f:
            f.write(updated_content)
        
        print("✅ API token updated in server.py")
        print()
        print("🎉 Setup complete! Now you can:")
        print("1. Start the backend: cd backend && python server.py")
        print("2. Start the frontend: cd lego_builder && npm run dev")
        print("3. Upload LEGO images to get real 3D models with Hunyuan3D-2!")
        print("4. Cost: ~$0.22 per 3D generation")
        
    except Exception as e:
        print(f"❌ Error updating server.py: {e}")

if __name__ == "__main__":
    setup_replicate()
