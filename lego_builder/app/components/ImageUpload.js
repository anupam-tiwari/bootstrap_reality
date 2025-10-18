'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Camera, Upload, X } from 'lucide-react';

export default function ImageUpload({ onImageUpload, isProcessing }) {
  const [preview, setPreview] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        const imageData = {
          file,
          url: reader.result,
          name: file.name,
          size: file.size
        };
        setPreview(imageData);
        onImageUpload(imageData);
      };
      reader.readAsDataURL(file);
    }
  }, [onImageUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp']
    },
    multiple: false,
    disabled: isProcessing
  });

  const clearImage = () => {
    setPreview(null);
    onImageUpload(null);
  };

  return (
    <div className="w-full">
      {!preview ? (
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
            ${isDragActive 
              ? 'border-blue-500 bg-blue-50' 
              : 'border-gray-300 hover:border-blue-400'
            }
            ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input {...getInputProps()} />
          <Camera className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <p className="text-lg font-medium text-gray-700 mb-2">
            {isDragActive ? 'Drop your LEGO photo here' : 'Upload LEGO Set Photo'}
          </p>
          <p className="text-sm text-gray-500">
            Drag & drop or click to select • JPG, PNG, GIF up to 10MB
          </p>
        </div>
      ) : (
        <div className="relative">
          <img
            src={preview.url}
            alt="LEGO set preview"
            className="w-full h-64 object-cover rounded-lg"
          />
          <button
            onClick={clearImage}
            className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
            disabled={isProcessing}
          >
            <X className="h-4 w-4" />
          </button>
          <div className="mt-2 text-sm text-gray-600">
            <p><strong>File:</strong> {preview.name}</p>
            <p><strong>Size:</strong> {(preview.size / 1024 / 1024).toFixed(2)} MB</p>
          </div>
        </div>
      )}
    </div>
  );
}
