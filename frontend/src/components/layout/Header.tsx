import React from 'react'

const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="header-left">
        <div className="logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="logo-icon">
            <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7S2 12 2 12z" />
            <circle cx="12" cy="12" r="3" />
          </svg>
          <span className="logo-text">Signal Processing Lab</span>
        </div>
      </div>
      <div className="header-right">
        <span className="version">v1.0</span>
      </div>
    </header>
  )
}

export default Header
