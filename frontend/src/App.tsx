import React, { useState } from 'react'
import Header from './components/layout/Header.tsx'
import NavigationTabs from './components/layout/NavigationTabs.tsx'
import ViewportSection from './components/mixer/ViewportSection.tsx'
import MixerSidebar from './components/mixer/MixerSidebar.tsx'
import OutputSection from './components/mixer/OutputSection.tsx'

export interface ImageData {
  id: number
  file: File | null
  originalUrl: string | null
  originalBase64: string | null
  ftMagnitudeUrl: string | null
  ftPhaseUrl: string | null
  ftRealUrl: string | null
  ftImaginaryUrl: string | null
  brightness: number
  contrast: number
}

export interface MixerSettings {
  componentWeights: { [key: number]: number }
  selectedComponent: 'magnitude' | 'phase' | 'real' | 'imaginary'
  regionType: 'full' | 'inner' | 'outer'
  regionSize: number
  outputPort: 1 | 2
}

function App() {
  const [activeTab, setActiveTab] = useState<'mixer' | 'beamforming'>('mixer')
  const [images, setImages] = useState<ImageData[]>([
    { id: 1, file: null, originalUrl: null, originalBase64: null, ftMagnitudeUrl: null, ftPhaseUrl: null, ftRealUrl: null, ftImaginaryUrl: null, brightness: 0, contrast: 0 },
    { id: 2, file: null, originalUrl: null, originalBase64: null, ftMagnitudeUrl: null, ftPhaseUrl: null, ftRealUrl: null, ftImaginaryUrl: null, brightness: 0, contrast: 0 },
    { id: 3, file: null, originalUrl: null, originalBase64: null, ftMagnitudeUrl: null, ftPhaseUrl: null, ftRealUrl: null, ftImaginaryUrl: null, brightness: 0, contrast: 0 },
    { id: 4, file: null, originalUrl: null, originalBase64: null, ftMagnitudeUrl: null, ftPhaseUrl: null, ftRealUrl: null, ftImaginaryUrl: null, brightness: 0, contrast: 0 },
  ])
  
  const [mixerSettings, setMixerSettings] = useState<MixerSettings>({
    componentWeights: { 1: 25, 2: 25, 3: 25, 4: 25 },
    selectedComponent: 'magnitude',
    regionType: 'full',
    regionSize: 50,
    outputPort: 1
  })

  const [outputImages, setOutputImages] = useState<{ output1: string | null; output2: string | null }>({
    output1: null,
    output2: null
  })

  const [isProcessing, setIsProcessing] = useState(false)

  const handleImageUpload = async (id: number, file: File) => {
    const formData = new FormData()
    formData.append('image', file)
    formData.append('imageId', id.toString())

    try {
      // Upload image - backend now handles FFT and returns all updated images
      const uploadResponse = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData
      })

      if (uploadResponse.ok) {
        const data = await uploadResponse.json()
        
        // Update all images that were resized
        setImages(prev => prev.map(img => {
          const updatedData = data.updatedImages?.[img.id.toString()]
          
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
            }
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
            }
          }
          return img
        }))
      }
    } catch (error) {
      console.error('Error uploading image:', error)
    }
  }

  const handleBrightnessContrastChange = async (id: number, brightness: number, contrast: number) => {
    const image = images.find(img => img.id === id)
    if (!image || !image.originalBase64) return

    try {
      const response = await fetch('http://localhost:5000/adjust_brightness_contrast', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          image: image.originalBase64,
          brightness,
          contrast
        })
      })

      if (response.ok) {
        const data = await response.json()
        setImages(prev => prev.map(img => 
          img.id === id 
            ? {
                ...img,
                originalUrl: `data:image/png;base64,${data.image}`,
                brightness,
                contrast
              }
            : img
        ))
      }
    } catch (error) {
      console.error('Error adjusting brightness/contrast:', error)
    }
  }

  const handleMix = async () => {
    setIsProcessing(true)
    
    try {
      const response = await fetch('http://localhost:5000/mix_images', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          images: images.filter(img => img.file !== null).map(img => ({
            id: img.id,
            weight: mixerSettings.componentWeights[img.id] / 100
          })),
          component: mixerSettings.selectedComponent,
          regionType: mixerSettings.regionType,
          regionSize: mixerSettings.regionSize / 100,
          outputPort: mixerSettings.outputPort
        })
      })

      if (response.ok) {
        const data = await response.json()
        const resultUrl = `data:image/png;base64,${data.result}`
        if (mixerSettings.outputPort === 1) {
          setOutputImages(prev => ({ ...prev, output1: resultUrl }))
        } else {
          setOutputImages(prev => ({ ...prev, output2: resultUrl }))
        }
      }
    } catch (error) {
      console.error('Error mixing images:', error)
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="app">
      <Header />
      <NavigationTabs activeTab={activeTab} onTabChange={setActiveTab} />
      
      {activeTab === 'mixer' && (
        <main className="main-content">
          <div className="mixer-layout">
            <ViewportSection 
              images={images} 
              onImageUpload={handleImageUpload}
              onBrightnessContrastChange={handleBrightnessContrastChange}
            />
            <MixerSidebar 
              settings={mixerSettings} 
              onSettingsChange={setMixerSettings}
              onMix={handleMix}
              isProcessing={isProcessing}
              images={images}
            />
            <OutputSection outputs={outputImages} />
          </div>
        </main>
      )}
      
      {activeTab === 'beamforming' && (
        <main className="main-content">
          <div className="coming-soon">
            <h2>Beamforming Simulator</h2>
            <p>Coming soon...</p>
          </div>
        </main>
      )}
    </div>
  )
}

export default App
