# Signal Processing Lab - FT Magnitude/Phase Mixer

A web application for exploring Fourier Transform components and mixing images based on their frequency domain representations.

## Features

### Image Viewers
- **4 Input Viewports**: Load and view up to 4 grayscale images simultaneously
- **Automatic Grayscale Conversion**: Colored images are automatically converted to grayscale
- **Unified Size**: All images are automatically resized to match the smallest image dimensions
- **FT Components Display**: View different Fourier Transform components:
  - FT Magnitude
  - FT Phase
  - FT Real
  - FT Imaginary
- **Drag & Drop Upload**: Easy image loading via drag and drop or click to browse
- **Brightness/Contrast Control**: Adjust image brightness and contrast via mouse drag

### Components Mixer
- **Weighted Mixing**: Combine FT components from multiple images using customizable weights
- **Component Selection**: Choose which FT component to mix (Magnitude, Phase, Real, Imaginary)
- **Real-time Sliders**: Adjust mixing weights with intuitive slider controls

### Region Mixer
- **Region Selection**: Select inner (low frequencies) or outer (high frequencies) regions
- **Customizable Region Size**: Adjust the region size percentage via slider
- **Unified Region**: Region settings apply to all images uniformly

### Output
- **Dual Output Ports**: Results can be displayed in one of two output viewports
- **Inverse FFT**: Mixed result is computed via inverse FFT

## Tech Stack

### Frontend
- React 18 with TypeScript
- Vite for build tooling
- CSS with CSS Variables for theming

### Backend
- Python Flask
- NumPy for numerical computations
- OpenCV for image processing
- Flask-CORS for cross-origin requests

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DSP_Task4
   ```

2. **Setup Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. **Start the Backend Server**
   ```bash
   cd backend
   python app.py
   ```
   The backend will run on `http://localhost:5000`

2. **Start the Frontend Development Server**
   ```bash
   cd frontend
   npm run dev
   ```
   The frontend will run on `http://localhost:3000`

3. **Open your browser** and navigate to `http://localhost:3000`

## Usage

1. **Upload Images**: Drag and drop images onto any of the 4 input viewports, or click to browse
2. **View FT Components**: Use the dropdown in each viewport to switch between Original, Magnitude, Phase, Real, and Imaginary views
3. **Adjust Brightness/Contrast**: Click and drag on an image to adjust brightness (vertical) and contrast (horizontal)
4. **Configure Mixer**: 
   - Select the FT component to mix
   - Adjust individual image weights using sliders
   - Choose region type (Full, Inner, Outer) and size
   - Select output port (1 or 2)
5. **Mix Images**: Click the "Mix Images" button to generate the mixed result

## Project Structure

```
DSP_Task4/
├── backend/
│   └── app.py              # Flask backend server
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/     # Header, Navigation components
│   │   │   └── mixer/      # Viewport, Sidebar, Controls components
│   │   ├── styles/
│   │   │   └── globals.css # Global styles with dark theme
│   │   ├── App.tsx         # Main application component
│   │   └── main.tsx        # Application entry point
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── project_specification.md
└── README.md
```

## License

This project is for educational purposes as part of a Digital Signal Processing course.
