# 🧱 LEGO Builder AI

A hackathon project that converts LEGO set photos into interactive 3D assets using AI-powered piece detection and 3D generation.

## 🚀 Features

- **AI-Powered Piece Detection**: Multiple detection methods including TRELLIS, Segment Anything, and YOLO
- **3D Asset Generation**: Convert detected pieces into 3D GLB assets
- **Interactive 3D Viewer**: Play with your LEGO pieces in a virtual environment
- **Asset Library**: Manage and organize your detected LEGO pieces
- **Multiple AI Models**: Choose from different detection approaches for optimal results

## 🛠️ Tech Stack

### Frontend
- **Next.js 15** - React framework
- **Three.js** - 3D graphics and visualization
- **React Three Fiber** - React integration for Three.js
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

### Backend
- **Flask** - Python web framework
- **Hugging Face API** - AI model integration
- **TRELLIS** - 3D asset generation
- **Segment Anything** - Image segmentation
- **YOLO** - Object detection

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Hugging Face API key (optional for demo mode)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd bootstrap_reality
   ```

2. **Install frontend dependencies**
   ```bash
   cd lego_builder
   npm install
   ```

3. **Install backend dependencies**
   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env.local` file in the `lego_builder` directory:
   ```env
   HUGGINGFACE_API_KEY=your_huggingface_api_key_here
   NODE_ENV=development
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   cd backend
   python server.py
   ```
   The backend will run on `http://localhost:5000`

2. **Start the frontend development server**
   ```bash
   cd lego_builder
   npm run dev
   ```
   The frontend will run on `http://localhost:3000`

## 🎯 How It Works

### 1. Image Upload
- Upload a photo of your LEGO set
- Supports JPG, PNG, GIF, and other common image formats
- Drag & drop or click to upload

### 2. AI Piece Detection
Choose from three detection methods:

- **TRELLIS (Recommended)**: Advanced AI for 3D asset generation
- **Segment Anything**: Meta's segmentation model for precise piece isolation
- **YOLO LEGO Detection**: Custom trained LEGO detector

### 3. 3D Asset Generation
- Each detected piece is converted into a 3D GLB asset
- Assets are stored in your personal library
- Download individual pieces or entire sets

### 4. Interactive 3D Builder
- Drag and drop pieces in the 3D viewer
- Rotate, zoom, and manipulate pieces
- Build virtual LEGO creations

## 🔧 API Integration

### TRELLIS Integration
The app integrates with [TRELLIS](https://huggingface.co/spaces/trellis-community/TRELLIS) for advanced 3D asset generation:

```javascript
// Example API call
const response = await fetch('/api/detect-pieces', {
  method: 'POST',
  body: formData
});
```

### Alternative AI Models
- **Segment Anything Model**: For precise piece segmentation
- **YOLO**: For object detection and classification
- **Custom LEGO Detection**: Specialized models for LEGO piece recognition

## 📁 Project Structure

```
bootstrap_reality/
├── lego_builder/                 # Next.js frontend
│   ├── app/
│   │   ├── components/          # React components
│   │   │   ├── ImageUpload.js
│   │   │   ├── PieceDetector.js
│   │   │   ├── AssetLibrary.js
│   │   │   └── ThreeDViewer.js
│   │   ├── api/                 # API routes
│   │   └── page.js             # Main page
│   └── package.json
├── backend/                     # Flask backend
│   ├── server.py              # Main server
│   └── requirements.txt
└── README.md
```

## 🎨 Customization

### Adding New Detection Methods
1. Create a new detection function in `server.py`
2. Add the method to the API route handler
3. Update the frontend component to include the new option

### Styling
- Modify `globals.css` for global styles
- Update component styles using Tailwind CSS classes
- Customize the 3D viewer appearance in `ThreeDViewer.js`

## 🚀 Deployment

### Frontend (Vercel)
```bash
cd lego_builder
npm run build
# Deploy to Vercel
```

### Backend (Railway/Heroku)
```bash
cd backend
# Deploy with your preferred platform
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [TRELLIS](https://huggingface.co/spaces/trellis-community/TRELLIS) for 3D asset generation
- [Hugging Face](https://huggingface.co/) for AI model APIs
- [Three.js](https://threejs.org/) for 3D graphics
- [React Three Fiber](https://docs.pmnd.rs/react-three-fiber) for React integration

## 🔮 Future Enhancements

- **Real-time Collaboration**: Multiple users building together
- **AR Integration**: Augmented reality LEGO building
- **AI Building Suggestions**: Smart recommendations for builds
- **Piece Recognition**: Identify specific LEGO piece numbers
- **Export Options**: 3D printing, VR, and more formats
