import React, { useState, useRef, useEffect } from 'react'
import Header from './components/layout/Header'
import NavigationTabs from './components/layout/NavigationTabs'
import ViewportSection from './components/mixer/ViewportSection'
import MixerSidebar from './components/mixer/MixerSidebar'
import OutputSection from './components/mixer/OutputSection'
import { BeamformingPage } from './components/beamforming'

function App() {
    const [activeTab, setActiveTab] = useState('mixer')
    const [images, setImages] = useState([
        { id: 1, file: null, originalUrl: null, originalBase64: null, ftMagnitudeUrl: null, ftPhaseUrl: null, ftRealUrl: null, ftImaginaryUrl: null, brightness: 0, contrast: 0 },
        { id: 2, file: null, originalUrl: null, originalBase64: null, ftMagnitudeUrl: null, ftPhaseUrl: null, ftRealUrl: null, ftImaginaryUrl: null, brightness: 0, contrast: 0 },
        { id: 3, file: null, originalUrl: null, originalBase64: null, ftMagnitudeUrl: null, ftPhaseUrl: null, ftRealUrl: null, ftImaginaryUrl: null, brightness: 0, contrast: 0 },
        { id: 4, file: null, originalUrl: null, originalBase64: null, ftMagnitudeUrl: null, ftPhaseUrl: null, ftRealUrl: null, ftImaginaryUrl: null, brightness: 0, contrast: 0 },
    ])

    const [mixerSettings, setMixerSettings] = useState({
        //initial weights for each component
        componentWeights: { 1: 25, 2: 25, 3: 25, 4: 25 },
        selectedComponent: 'magnitude',
        regionType: 'full',
        regionSize: 50,
        outputPort: 1
    })

    const [outputImages, setOutputImages] = useState({
        output1: null,
        output2: null
    })

    const [isProcessing, setIsProcessing] = useState(false)

    // Unified Region of Interest selection
    const [unifiedRoi, setUnifiedRoi] = useState({
        x: 25, y: 25, width: 50, height: 50, mode: 'inner'
    })

    const handleRegionSelect = (roi) => {
        setUnifiedRoi(prev => ({
            ...prev,
            ...roi
        }))
    }

    const handleImageUpload = async (id, file) => {
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

    const handleBrightnessContrastChange = async (id, brightness, contrast) => {
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

    // Track the latest mixing request to avoid race conditions
    const mixRequestRef = useRef(0)

    // Real-time mixing logic with debounce and cancellation
    useEffect(() => {
        // Only mix if at least one image is uploaded
        if (images.every(img => img.file === null)) return

        const controller = new AbortController()
        const requestId = ++mixRequestRef.current

        const timer = setTimeout(() => {
            handleMix(controller.signal, requestId)
        }, 400) // 400ms debounce for stability

        return () => {
            clearTimeout(timer)
            controller.abort()
        }
    }, [
        mixerSettings.componentWeights,
        mixerSettings.selectedComponent,
        mixerSettings.regionType,
        mixerSettings.regionSize,
        unifiedRoi,
        images.map(img => img.originalBase64).join(',')
    ])

    const handleMix = async (signal, requestId) => {
        setIsProcessing(true)

        try {
            const response = await fetch('http://localhost:5000/mix_images', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                signal, // Pass the abort signal
                body: JSON.stringify({
                    images: images.filter(img => img.file !== null).map(img => ({
                        id: img.id,
                        weight: mixerSettings.componentWeights[img.id] / 100,
                        roi: unifiedRoi
                    })),
                    component: mixerSettings.selectedComponent,
                    regionType: mixerSettings.regionType,
                    regionSize: mixerSettings.regionSize / 100,
                    outputPort: mixerSettings.outputPort
                })
            })

            if (!response.ok) return

            // If a newer request has already started, ignore this one
            if (requestId !== mixRequestRef.current) return

            const result = await response.json()
            if (result.success) {
                const resultUrl = `data:image/png;base64,${result.result}`
                if (mixerSettings.outputPort === 1) {
                    setOutputImages(prev => ({ ...prev, output1: resultUrl }))
                } else {
                    setOutputImages(prev => ({ ...prev, output2: resultUrl }))
                }
            }
        } catch (error) {
            if (error.name === 'AbortError') return
            console.error('Error mixing images:', error)
        } finally {
            // Only stop processing indicator if this was the latest request
            if (requestId === mixRequestRef.current) {
                setIsProcessing(false)
            }
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
                            unifiedRoi={unifiedRoi}
                            onImageUpload={handleImageUpload}
                            onBrightnessContrastChange={handleBrightnessContrastChange}
                            onRegionSelect={handleRegionSelect}
                        />
                        <MixerSidebar
                            settings={mixerSettings}
                            onSettingsChange={setMixerSettings}
                            onMix={handleMix}
                            isProcessing={isProcessing}
                            images={images}
                            unifiedRoi={unifiedRoi}
                            onRoiChange={handleRegionSelect}
                        />
                        <OutputSection outputs={outputImages} />
                    </div>
                </main>
            )}

            {activeTab === 'beamforming' && (
                <BeamformingPage />
            )}
        </div>
    )
}

export default App
