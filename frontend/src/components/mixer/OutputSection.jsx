import React from 'react'
import OutputViewport from './cards/OutputViewport'

const OutputSection = ({ outputs }) => {
    return (
        <section className="output-section">
            <div className="section-header">
                <h2>Output</h2>
                <span className="section-badge">2 Ports</span>
            </div>
            <div className="output-grid">
                <OutputViewport label="Output 1" imageUrl={outputs.output1} />
                <OutputViewport label="Output 2" imageUrl={outputs.output2} />
            </div>
        </section>
    )
}

export default OutputSection
