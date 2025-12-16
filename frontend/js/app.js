// Application State
const state = {
  activeTab: 'mixer',
  images: [
    { id: 1, file: null, originalUrl: null, originalBase64: null, ftMagnitudeUrl: null, ftPhaseUrl: null, ftRealUrl: null, ftImaginaryUrl: null, brightness: 0, contrast: 0 },
    { id: 2, file: null, originalUrl: null, originalBase64: null, ftMagnitudeUrl: null, ftPhaseUrl: null, ftRealUrl: null, ftImaginaryUrl: null, brightness: 0, contrast: 0 },
    { id: 3, file: null, originalUrl: null, originalBase64: null, ftMagnitudeUrl: null, ftPhaseUrl: null, ftRealUrl: null, ftImaginaryUrl: null, brightness: 0, contrast: 0 },
    { id: 4, file: null, originalUrl: null, originalBase64: null, ftMagnitudeUrl: null, ftPhaseUrl: null, ftRealUrl: null, ftImaginaryUrl: null, brightness: 0, contrast: 0 }
  ],
  mixerSettings: {
    componentWeights: { 1: 25, 2: 25, 3: 25, 4: 25 },
    selectedComponent: 'magnitude',
    regionType: 'full',
    regionSize: 50,
    outputPort: 1
  },
  outputImages: {
    output1: null,
    output2: null
  },
  isProcessing: false
};

// API Base URL
const API_BASE_URL = 'http://localhost:5000';

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
  initializeNavigation();
  initializeImageViewports();
  initializeMixerControls();
  initializeOutputSection();
});

// Navigation
function initializeNavigation() {
  const navTabs = document.querySelectorAll('.nav-tab');
  
  navTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const tabName = tab.getAttribute('data-tab');
      setActiveTab(tabName);
    });
  });
}

function setActiveTab(tabName) {
  state.activeTab = tabName;
  
  // Update tab styling
  document.querySelectorAll('.nav-tab').forEach(tab => {
    if (tab.getAttribute('data-tab') === tabName) {
      tab.classList.add('active');
    } else {
      tab.classList.remove('active');
    }
  });
  
  // Update content visibility
  document.getElementById('mixer-content').style.display = tabName === 'mixer' ? 'block' : 'none';
  document.getElementById('beamforming-content').style.display = tabName === 'beamforming' ? 'block' : 'none';
}

// Image Viewports
function initializeImageViewports() {
  const viewports = document.querySelectorAll('.image-viewport');
  
  viewports.forEach(viewport => {
    const imageId = parseInt(viewport.getAttribute('data-image-id'));
    const viewportContent = viewport.querySelector('.viewport-content');
    const fileInput = viewport.querySelector('input[type="file"]');
    const uploadPlaceholder = viewport.querySelector('.upload-placeholder');
    const viewModeSelect = viewport.querySelector('.view-mode-select');
    
    // File input change
    fileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        handleImageUpload(imageId, file);
      }
    });
    
    // Click to upload
    if (uploadPlaceholder) {
      uploadPlaceholder.addEventListener('click', () => {
        fileInput.click();
      });
    }
    
    // Drag and drop
    viewportContent.addEventListener('dragover', (e) => {
      e.preventDefault();
      viewportContent.classList.add('dragging');
    });
    
    viewportContent.addEventListener('dragleave', () => {
      viewportContent.classList.remove('dragging');
    });
    
    viewportContent.addEventListener('drop', (e) => {
      e.preventDefault();
      viewportContent.classList.remove('dragging');
      
      const file = e.dataTransfer.files[0];
      if (file && file.type.startsWith('image/')) {
        handleImageUpload(imageId, file);
      }
    });
    
    // Double click to replace image
    viewportContent.addEventListener('dblclick', () => {
      const image = state.images.find(img => img.id === imageId);
      if (image && image.file) {
        fileInput.click();
      }
    });
    
    // View mode selection
    viewModeSelect.addEventListener('change', (e) => {
      updateViewportImage(imageId, e.target.value);
    });
    
    // Brightness/Contrast adjustment
    let isAdjusting = false;
    let adjustStart = null;
    let localBrightness = 0;
    let localContrast = 0;
    
    viewportContent.addEventListener('mousedown', (e) => {
      const image = state.images.find(img => img.id === imageId);
      if (!image || !image.file || !image.originalUrl) return;
      
      // Right click or Ctrl+Left click
      if (e.button === 2 || (e.button === 0 && e.ctrlKey)) {
        e.preventDefault();
        isAdjusting = true;
        viewportContent.classList.add('adjusting');
        
        localBrightness = image.brightness;
        localContrast = image.contrast;
        adjustStart = {
          x: e.clientX,
          y: e.clientY,
          brightness: localBrightness,
          contrast: localContrast
        };
      }
    });
    
    viewportContent.addEventListener('mousemove', (e) => {
      if (!isAdjusting || !adjustStart) return;
      
      const deltaX = e.clientX - adjustStart.x;
      const deltaY = e.clientY - adjustStart.y;
      
      // Horizontal movement controls contrast, vertical controls brightness
      localContrast = Math.max(-100, Math.min(100, adjustStart.contrast + deltaX * 0.5));
      localBrightness = Math.max(-100, Math.min(100, adjustStart.brightness - deltaY * 0.5));
      
      updateBrightnessContrastIndicator(imageId, localBrightness, localContrast);
    });
    
    const finishAdjustment = () => {
      if (isAdjusting) {
        isAdjusting = false;
        viewportContent.classList.remove('adjusting');
        handleBrightnessContrastChange(imageId, localBrightness, localContrast);
        adjustStart = null;
      }
    };
    
    viewportContent.addEventListener('mouseup', finishAdjustment);
    viewportContent.addEventListener('mouseleave', finishAdjustment);
    
    // Prevent context menu on right click when image is loaded
    viewportContent.addEventListener('contextmenu', (e) => {
      const image = state.images.find(img => img.id === imageId);
      if (image && image.file) {
        e.preventDefault();
      }
    });
  });
}

// Handle Image Upload
async function handleImageUpload(id, file) {
  const formData = new FormData();
  formData.append('image', file);
  formData.append('imageId', id.toString());
  
  try {
    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData
    });
    
    if (response.ok) {
      const data = await response.json();
      
      // Update all images that were resized
      state.images = state.images.map(img => {
        const updatedData = data.updatedImages?.[img.id.toString()];
        
        if (img.id === id) {
          // This is the newly uploaded image
          return {
            ...img,
            file,
            originalUrl: `data:image/png;base64,${data.image}`,
            originalBase64: data.image,
            ftMagnitudeUrl: `data:image/png;base64,${data.magnitude}`,
            ftPhaseUrl: `data:image/png;base64,${data.phase}`,
            ftRealUrl: `data:image/png;base64,${data.real}`,
            ftImaginaryUrl: `data:image/png;base64,${data.imaginary}`,
            brightness: 0,
            contrast: 0
          };
        } else if (updatedData && img.file) {
          // This is an existing image that was resized
          return {
            ...img,
            originalUrl: `data:image/png;base64,${updatedData.image}`,
            originalBase64: updatedData.image,
            ftMagnitudeUrl: `data:image/png;base64,${updatedData.magnitude}`,
            ftPhaseUrl: `data:image/png;base64,${updatedData.phase}`,
            ftRealUrl: `data:image/png;base64,${updatedData.real}`,
            ftImaginaryUrl: `data:image/png;base64,${updatedData.imaginary}`,
            brightness: 0,
            contrast: 0
          };
        }
        return img;
      });
      
      renderImageViewports();
      updateMixButtonState();
    }
  } catch (error) {
    console.error('Error uploading image:', error);
  }
}

// Handle Brightness/Contrast Change
async function handleBrightnessContrastChange(id, brightness, contrast) {
  const image = state.images.find(img => img.id === id);
  if (!image || !image.originalBase64) return;
  
  try {
    const response = await fetch(`${API_BASE_URL}/adjust_brightness_contrast`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        image: image.originalBase64,
        brightness,
        contrast
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      state.images = state.images.map(img =>
        img.id === id
          ? {
              ...img,
              originalUrl: `data:image/png;base64,${data.image}`,
              brightness,
              contrast
            }
          : img
      );
      
      renderImageViewports();
    }
  } catch (error) {
    console.error('Error adjusting brightness/contrast:', error);
  }
}

// Update Brightness/Contrast Indicator (live update during drag)
function updateBrightnessContrastIndicator(id, brightness, contrast) {
  const viewport = document.querySelector(`.image-viewport[data-image-id="${id}"]`);
  const indicator = viewport.querySelector('.bc-indicator');
  
  if (indicator) {
    indicator.textContent = `B:${Math.round(brightness)} C:${Math.round(contrast)}`;
  }
}

// Update Viewport Image based on view mode
function updateViewportImage(imageId, viewMode) {
  const image = state.images.find(img => img.id === imageId);
  if (!image) return;
  
  let imageUrl = null;
  switch (viewMode) {
    case 'original': imageUrl = image.originalUrl; break;
    case 'magnitude': imageUrl = image.ftMagnitudeUrl; break;
    case 'phase': imageUrl = image.ftPhaseUrl; break;
    case 'real': imageUrl = image.ftRealUrl; break;
    case 'imaginary': imageUrl = image.ftImaginaryUrl; break;
  }
  
  const viewport = document.querySelector(`.image-viewport[data-image-id="${imageId}"]`);
  const viewportContent = viewport.querySelector('.viewport-content');
  const img = viewportContent.querySelector('img');
  
  if (img && imageUrl) {
    img.src = imageUrl;
    img.alt = `Image ${imageId} - ${viewMode}`;
  }
}

// Render Image Viewports
function renderImageViewports() {
  state.images.forEach(image => {
    const viewport = document.querySelector(`.image-viewport[data-image-id="${image.id}"]`);
    const viewportContent = viewport.querySelector('.viewport-content');
    const uploadPlaceholder = viewport.querySelector('.upload-placeholder');
    const fileInput = viewport.querySelector('input[type="file"]');
    const viewModeSelect = viewport.querySelector('.view-mode-select');
    const bcIndicator = viewport.querySelector('.bc-indicator');
    
    // Clear existing content
    while (viewportContent.firstChild) {
      viewportContent.removeChild(viewportContent.firstChild);
    }
    
    if (image.file && image.originalUrl) {
      // Show image
      const img = document.createElement('img');
      const viewMode = viewModeSelect.value;
      
      let imageUrl = null;
      switch (viewMode) {
        case 'original': imageUrl = image.originalUrl; break;
        case 'magnitude': imageUrl = image.ftMagnitudeUrl; break;
        case 'phase': imageUrl = image.ftPhaseUrl; break;
        case 'real': imageUrl = image.ftRealUrl; break;
        case 'imaginary': imageUrl = image.ftImaginaryUrl; break;
      }
      
      if (imageUrl) {
        img.src = imageUrl;
        img.alt = `Image ${image.id} - ${viewMode}`;
        img.draggable = false;
        viewportContent.appendChild(img);
      }
      
      // Enable view mode select
      viewModeSelect.disabled = false;
      
      // Show B/C indicator
      bcIndicator.style.display = 'block';
      bcIndicator.textContent = `B:${Math.round(image.brightness)} C:${Math.round(image.contrast)}`;
      
      // Enable weight slider
      const weightSlider = document.querySelector(`.weight-slider[data-image-id="${image.id}"]`);
      const inactiveBadge = weightSlider.closest('.weight-slider-row').querySelector('.inactive-badge');
      weightSlider.disabled = false;
      if (inactiveBadge) {
        inactiveBadge.style.display = 'none';
      }
    } else {
      // Show upload placeholder
      const placeholder = uploadPlaceholder.cloneNode(true);
      viewportContent.appendChild(placeholder);
      
      // Setup click handler for cloned placeholder
      placeholder.addEventListener('click', () => {
        fileInput.click();
      });
      
      // Disable view mode select
      viewModeSelect.disabled = true;
      viewModeSelect.value = 'original';
      
      // Hide B/C indicator
      bcIndicator.style.display = 'none';
      
      // Disable weight slider
      const weightSlider = document.querySelector(`.weight-slider[data-image-id="${image.id}"]`);
      const inactiveBadge = weightSlider.closest('.weight-slider-row').querySelector('.inactive-badge');
      weightSlider.disabled = true;
      if (inactiveBadge) {
        inactiveBadge.style.display = 'inline';
      }
    }
    
    // Re-append file input
    viewportContent.appendChild(fileInput);
  });
}

// Initialize Mixer Controls
function initializeMixerControls() {
  // Component selector
  const componentSelect = document.getElementById('component-select');
  componentSelect.addEventListener('change', (e) => {
    state.mixerSettings.selectedComponent = e.target.value;
  });
  
  // Weight sliders
  const weightSliders = document.querySelectorAll('.weight-slider');
  weightSliders.forEach(slider => {
    const imageId = parseInt(slider.getAttribute('data-image-id'));
    
    slider.addEventListener('input', (e) => {
      const value = parseInt(e.target.value);
      state.mixerSettings.componentWeights[imageId] = value;
      
      // Update value display
      const valueDisplay = slider.closest('.weight-slider-row').querySelector('.weight-value');
      valueDisplay.textContent = `${value}%`;
    });
  });
  
  // Region type buttons
  const regionButtons = document.querySelectorAll('.region-btn');
  regionButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const regionType = btn.getAttribute('data-region');
      state.mixerSettings.regionType = regionType;
      
      // Update active state
      regionButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      // Show/hide region size control
      const regionSizeControl = document.getElementById('region-size-control');
      if (regionType === 'full') {
        regionSizeControl.style.display = 'none';
      } else {
        regionSizeControl.style.display = 'block';
      }
    });
  });
  
  // Region size slider
  const regionSizeSlider = document.getElementById('region-size-slider');
  const regionSizeValue = document.getElementById('region-size-value');
  
  regionSizeSlider.addEventListener('input', (e) => {
    const value = parseInt(e.target.value);
    state.mixerSettings.regionSize = value;
    regionSizeValue.textContent = `${value}%`;
  });
  
  // Output port buttons
  const outputButtons = document.querySelectorAll('.output-btn');
  outputButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const outputPort = parseInt(btn.getAttribute('data-output'));
      state.mixerSettings.outputPort = outputPort;
      
      // Update active state
      outputButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });
  
  // Mix button
  const mixButton = document.getElementById('mix-button');
  mixButton.addEventListener('click', handleMix);
}

// Handle Mix
async function handleMix() {
  state.isProcessing = true;
  updateMixButtonState();
  
  try {
    const response = await fetch(`${API_BASE_URL}/mix_images`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        images: state.images.filter(img => img.file !== null).map(img => ({
          id: img.id,
          weight: state.mixerSettings.componentWeights[img.id] / 100
        })),
        component: state.mixerSettings.selectedComponent,
        regionType: state.mixerSettings.regionType,
        regionSize: state.mixerSettings.regionSize / 100,
        outputPort: state.mixerSettings.outputPort
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      const resultUrl = `data:image/png;base64,${data.result}`;
      
      if (state.mixerSettings.outputPort === 1) {
        state.outputImages.output1 = resultUrl;
      } else {
        state.outputImages.output2 = resultUrl;
      }
      
      renderOutputSection();
    }
  } catch (error) {
    console.error('Error mixing images:', error);
  } finally {
    state.isProcessing = false;
    updateMixButtonState();
  }
}

// Update Mix Button State
function updateMixButtonState() {
  const mixButton = document.getElementById('mix-button');
  const hasImages = state.images.some(img => img.file !== null);
  
  if (state.isProcessing) {
    mixButton.disabled = true;
    mixButton.innerHTML = `
      <span class="spinner"></span>
      Processing...
    `;
  } else if (hasImages) {
    mixButton.disabled = false;
    mixButton.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mix-icon">
        <polygon points="5 3 19 12 5 21 5 3" />
      </svg>
      Mix Images
    `;
  } else {
    mixButton.disabled = true;
    mixButton.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mix-icon">
        <polygon points="5 3 19 12 5 21 5 3" />
      </svg>
      Mix Images
    `;
  }
}

// Initialize Output Section
function initializeOutputSection() {
  renderOutputSection();
}

// Render Output Section
function renderOutputSection() {
  [1, 2].forEach(outputId => {
    const outputViewport = document.querySelector(`.output-viewport[data-output-id="${outputId}"]`);
    const viewportContent = outputViewport.querySelector('.viewport-content');
    const outputKey = `output${outputId}`;
    const imageUrl = state.outputImages[outputKey];
    
    // Clear existing content
    while (viewportContent.firstChild) {
      viewportContent.removeChild(viewportContent.firstChild);
    }
    
    if (imageUrl) {
      // Show image
      const img = document.createElement('img');
      img.src = imageUrl;
      img.alt = `Output ${outputId}`;
      viewportContent.appendChild(img);
    } else {
      // Show empty state
      const emptyOutput = document.createElement('div');
      emptyOutput.className = 'empty-output';
      emptyOutput.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="empty-icon">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <polyline points="21 15 16 10 5 21" />
        </svg>
        <p>Output will appear here</p>
      `;
      viewportContent.appendChild(emptyOutput);
    }
  });
}
