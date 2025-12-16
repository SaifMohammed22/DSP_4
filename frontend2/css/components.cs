/* Button Components */
.btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: var(--border-radius-sm);
    font-family: inherit;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-normal);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    outline: none;
}

.btn:focus {
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.3);
}

.btn-primary {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
    color: white;
    box-shadow: var(--shadow-md);
}

.btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-lg);
}

.btn-primary:active {
    transform: translateY(0);
}

.btn-secondary {
    background: var(--bg-tertiary);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
}

.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: var(--primary-color);
}

.btn-outline {
    background: transparent;
    color: var(--text-primary);
    border: 1px solid var(--border-color);
}

.btn-outline:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: var(--primary-color);
}

.btn-danger {
    background: var(--danger-color);
    color: white;
}

.btn-danger:hover {
    background: #dc2626;
}

.btn-success {
    background: var(--success-color);
    color: white;
}

.btn-success:hover {
    background: #0da271;
}

.btn-sm {
    padding: 0.375rem 0.75rem;
    font-size: 0.75rem;
}

.btn-lg {
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
}

.btn-large {
    padding: 1rem 2rem;
    font-size: 1rem;
    font-weight: 600;
}

.btn-icon {
    padding: 0.5rem;
    width: 36px;
    height: 36px;
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none !important;
}

/* Form Components */
select {
    padding: 0.5rem 2.5rem 0.5rem 0.75rem;
    background: var(--bg-tertiary) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E") no-repeat right 0.75rem center;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-sm);
    color: var(--text-primary);
    font-family: inherit;
    font-size: 0.875rem;
    appearance: none;
    cursor: pointer;
    transition: border-color var(--transition-normal);
}

select:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
}

select:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

input[type="number"] {
    padding: 0.5rem 0.75rem;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-sm);
    color: var(--text-primary);
    font-family: 'Monaco', 'Courier New', monospace;
    font-size: 0.875rem;
    transition: border-color var(--transition-normal);
}

input[type="number"]:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
}

input[type="number"]:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Checkbox & Radio */
.checkbox-container,
.radio-container {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    font-size: 0.875rem;
    color: var(--text-secondary);
    user-select: none;
}

.checkbox-container input,
.radio-container input {
    position: absolute;
    opacity: 0;
    cursor: pointer;
}

.checkbox-custom,
.radio-custom {
    width: 18px;
    height: 18px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: 3px;
    position: relative;
    transition: all var(--transition-normal);
}

.radio-custom {
    border-radius: 50%;
}

.checkbox-container:hover .checkbox-custom,
.radio-container:hover .radio-custom {
    border-color: var(--primary-color);
}

.checkbox-container input:checked ~ .checkbox-custom,
.radio-container input:checked ~ .radio-custom {
    background: var(--primary-color);
    border-color: var(--primary-color);
}

.checkbox-custom::after {
    content: '';
    position: absolute;
    display: none;
    left: 6px;
    top: 2px;
    width: 5px;
    height: 10px;
    border: solid white;
    border-width: 0 2px 2px 0;
    transform: rotate(45deg);
}

.radio-custom::after {
    content: '';
    position: absolute;
    display: none;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 8px;
    height: 8px;
    background: white;
    border-radius: 50%;
}

.checkbox-container input:checked ~ .checkbox-custom::after,
.radio-container input:checked ~ .radio-custom::after {
    display: block;
}

/* Toggle Switch */
.toggle-container {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
}

.toggle-switch {
    position: relative;
    width: 44px;
    height: 24px;
}

.toggle-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.toggle-slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    transition: var(--transition-normal);
    border-radius: 24px;
}

.toggle-slider:before {
    position: absolute;
    content: "";
    height: 16px;
    width: 16px;
    left: 3px;
    bottom: 3px;
    background: white;
    transition: var(--transition-normal);
    border-radius: 50%;
}

input:checked + .toggle-slider {
    background: var(--primary-color);
    border-color: var(--primary-color);
}

input:checked + .toggle-slider:before {
    transform: translateX(20px);
}

.toggle-label {
    font-size: 0.875rem;
    color: var(--text-secondary);
}

/* Card Components */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    transition: all var(--transition-normal);
}

.card:hover {
    border-color: var(--primary-color);
    box-shadow: var(--shadow-lg);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border-color);
}

.card-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.card-actions {
    display: flex;
    gap: 0.5rem;
}

/* Alert Components */
.alert {
    padding: 1rem;
    border-radius: var(--border-radius);
    margin-bottom: 1rem;
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    border: 1px solid transparent;
}

.alert-icon {
    font-size: 1.25rem;
    flex-shrink: 0;
}

.alert-content {
    flex: 1;
}

.alert-title {
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.alert-message {
    font-size: 0.875rem;
    opacity: 0.9;
}

.alert-info {
    background: rgba(6, 182, 212, 0.1);
    border-color: rgba(6, 182, 212, 0.3);
    color: var(--accent-color);
}

.alert-success {
    background: rgba(16, 185, 129, 0.1);
    border-color: rgba(16, 185, 129, 0.3);
    color: var(--success-color);
}

.alert-warning {
    background: rgba(245, 158, 11, 0.1);
    border-color: rgba(245, 158, 11, 0.3);
    color: var(--warning-color);
}

.alert-danger {
    background: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.3);
    color: var(--danger-color);
}

/* Badge Components */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
    line-height: 1;
}

.badge-primary {
    background: rgba(37, 99, 235, 0.2);
    color: var(--primary-color);
    border: 1px solid rgba(37, 99, 235, 0.3);
}

.badge-success {
    background: rgba(16, 185, 129, 0.2);
    color: var(--success-color);
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.badge-warning {
    background: rgba(245, 158, 11, 0.2);
    color: var(--warning-color);
    border: 1px solid rgba(245, 158, 11, 0.3);
}

.badge-danger {
    background: rgba(239, 68, 68, 0.2);
    color: var(--danger-color);
    border: 1px solid rgba(239, 68, 68, 0.3);
}

/* Loading Spinner */
.spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border-color);
    border-top-color: var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

.spinner-sm {
    width: 20px;
    height: 20px;
    border-width: 2px;
}

.spinner-lg {
    width: 60px;
    height: 60px;
    border-width: 4px;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

/* Modal */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    opacity: 0;
    visibility: hidden;
    transition: all var(--transition-normal);
}

.modal-overlay.active {
    opacity: 1;
    visibility: visible;
}

.modal {
    background: var(--bg-card);
    border-radius: var(--border-radius);
    width: 90%;
    max-width: 500px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    transform: translateY(-20px);
    transition: transform var(--transition-normal);
    overflow: hidden;
    box-shadow: var(--shadow-lg);
}

.modal-overlay.active .modal {
    transform: translateY(0);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid var(--border-color);
}

.modal-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary);
}

.modal-close {
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    padding: 0.5rem;
    border-radius: var(--border-radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-normal);
}

.modal-close:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
}

.modal-content {
    padding: 1.5rem;
    overflow-y: auto;
    flex: 1;
}

.modal-footer {
    padding: 1.5rem;
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
}

/* Tooltip */
.tooltip {
    position: absolute;
    background: var(--bg-primary);
    color: var(--text-primary);
    padding: 0.5rem 0.75rem;
    border-radius: var(--border-radius-sm);
    font-size: 0.75rem;
    white-space: nowrap;
    z-index: 1000;
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow-lg);
    pointer-events: none;
    opacity: 0;
    transition: opacity var(--transition-normal);
}

.tooltip.active {
    opacity: 1;
}

.tooltip-arrow {
    position: absolute;
    width: 10px;
    height: 10px;
    background: var(--bg-primary);
    transform: rotate(45deg);
    border: 1px solid var(--border-color);
    border-top: none;
    border-left: none;
}

/* Context Menu */
.context-menu {
    position: fixed;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-lg);
    z-index: 1000;
    min-width: 150px;
    opacity: 0;
    visibility: hidden;
    transform: scale(0.95);
    transition: all var(--transition-normal);
}

.context-menu.active {
    opacity: 1;
    visibility: visible;
    transform: scale(1);
}

.context-menu-item {
    padding: 0.5rem 1rem;
    cursor: pointer;
    transition: background var(--transition-normal);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: var(--text-primary);
}

.context-menu-item:hover {
    background: var(--bg-tertiary);
}

.context-menu-divider {
    height: 1px;
    background: var(--border-color);
    margin: 0.25rem 0;
}

/* Dropdown */
.dropdown {
    position: relative;
}

.dropdown-toggle {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.dropdown-menu {
    position: absolute;
    top: 100%;
    right: 0;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-lg);
    min-width: 200px;
    z-index: 1000;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px);
    transition: all var(--transition-normal);
}

.dropdown-menu.active {
    opacity: 1;
    visibility: visible;
    transform: translateY(5px);
}

.dropdown-item {
    padding: 0.75rem 1rem;
    cursor: pointer;
    transition: background var(--transition-normal);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: var(--text-primary);
}

.dropdown-item:hover {
    background: var(--bg-tertiary);
}

.dropdown-divider {
    height: 1px;
    background: var(--border-color);
    margin: 0.25rem 0;
}