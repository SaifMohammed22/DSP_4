from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime

class ArrayType(str, Enum):
    LINEAR = "linear"
    CURVED = "curved"
    CIRCULAR = "circular"
    RECTANGULAR = "rectangular"
    SPIRAL = "spiral"
    RANDOM = "random"

class SourceType(str, Enum):
    TRANSMITTER = "transmitter"
    RECEIVER = "receiver"
    TARGET = "target"
    INTERFERENCE = "interference"
    JAMMER = "jammer"

class ArrayConfig(BaseModel):
    """Configuration for a phased array"""
    array_id: Optional[str] = Field(None, description="Unique array identifier")
    type: ArrayType = Field(ArrayType.LINEAR, description="Array geometry type")
    num_elements: int = Field(8, ge=1, le=1000, description="Number of elements")
    spacing: float = Field(0.5, ge=0.1, le=10.0, description="Element spacing in wavelengths")
    position: List[float] = Field([0.0, 0.0], min_items=2, max_items=2, description="Array position [x, y]")
    orientation: float = Field(0.0, ge=-180.0, le=180.0, description="Orientation in degrees")
    curvature: float = Field(0.0, ge=0.0, le=1.0, description="Curvature parameter")
    delays: Optional[List[float]] = Field(None, description="Custom delays for each element")
    amplitudes: Optional[List[float]] = Field(None, description="Amplitudes for each element")
    enabled: bool = Field(True, description="Whether array is enabled")
    
    @validator('delays')
    def validate_delays(cls, v, values):
        if v is not None:
            num_elements = values.get('num_elements', 8)
            if len(v) != num_elements:
                raise ValueError(f'Delays must have {num_elements} elements')
        return v
    
    @validator('amplitudes')
    def validate_amplitudes(cls, v, values):
        if v is not None:
            num_elements = values.get('num_elements', 8)
            if len(v) != num_elements:
                raise ValueError(f'Amplitudes must have {num_elements} elements')
        return v

class SourceConfig(BaseModel):
    """Configuration for a signal source"""
    source_id: Optional[str] = Field(None, description="Unique source identifier")
    type: SourceType = Field(SourceType.TRANSMITTER, description="Type of source")
    position: List[float] = Field([0.0, 0.0], min_items=2, max_items=2, description="Source position [x, y]")
    frequency: float = Field(2.4e9, ge=1e6, le=100e9, description="Frequency in Hz")
    amplitude: float = Field(1.0, ge=0.0, le=10.0, description="Source amplitude")
    phase: float = Field(0.0, description="Initial phase in radians")
    orientation: float = Field(0.0, ge=-180.0, le=180.0, description="Orientation in degrees")
    enabled: bool = Field(True, description="Whether source is enabled")

class SimulationRequest(BaseModel):
    """Request for beamforming simulation"""
    arrays: List[ArrayConfig] = Field(..., min_items=1, description="Array configurations")
    sources: Optional[List[SourceConfig]] = Field([], description="Source configurations")
    frequencies: List[float] = Field([2.4e9], min_items=1, description="Frequencies in Hz")
    steering_angle: float = Field(0.0, ge=-90.0, le=90.0, description="Steering angle in degrees")
    grid_size: int = Field(200, ge=50, le=1000, description="Grid size for simulation")
    grid_range: float = Field(10.0, ge=1.0, le=1000.0, description="Grid range in meters")
    include_interference: bool = Field(True, description="Include interference calculation")
    
    class Config:
        schema_extra = {
            "example": {
                "arrays": [
                    {
                        "type": "linear",
                        "num_elements": 8,
                        "spacing": 0.5,
                        "position": [0, 0],
                        "orientation": 0
                    }
                ],
                "frequencies": [2.4e9],
                "steering_angle": 30.0,
                "grid_size": 200,
                "grid_range": 10.0
            }
        }

class SteeringRequest(BaseModel):
    """Request for beam steering"""
    steering_angle: float = Field(..., ge=-90.0, le=90.0, description="New steering angle in degrees")
    array_id: Optional[str] = Field(None, description="Specific array to steer (all if None)")

class ScenarioRequest(BaseModel):
    """Request to load a scenario"""
    scenario_name: str = Field(..., description="Name of scenario to load")
    custom_parameters: Optional[Dict[str, Any]] = Field(None, description="Custom parameters to override")

class ScenarioSaveRequest(BaseModel):
    """Request to save a scenario"""
    name: str = Field(..., min_length=1, max_length=100, description="Scenario name")
    description: str = Field("", max_length=500, description="Scenario description")
    arrays: List[ArrayConfig] = Field(..., description="Array configurations")
    sources: List[SourceConfig] = Field([], description="Source configurations")
    frequencies: List[float] = Field([2.4e9], description="Operating frequencies")

class BeamformingResponse(BaseModel):
    """Response for beamforming simulation"""
    task_id: str = Field(..., description="Task identifier for async processing")
    status: str = Field("processing", description="Task status")
    message: str = Field("", description="Status message")
    estimated_time: Optional[float] = Field(None, description="Estimated completion time in seconds")

class SimulationResult(BaseModel):
    """Detailed simulation results"""
    beam_pattern: Optional[Dict[str, Any]] = Field(None, description="Beam pattern data")
    interference_map: Optional[Dict[str, Any]] = Field(None, description="Interference map data")
    array_positions: List[List[float]] = Field([], description="Element positions for each array")
    source_positions: List[List[float]] = Field([], description="Source positions")
    performance_metrics: Optional[Dict[str, Any]] = Field(None, description="Performance metrics")
    visualization_data: Optional[Dict[str, Any]] = Field(None, description="Visualization data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Result timestamp")

class TaskStatusResponse(BaseModel):
    """Response for task status check"""
    task_id: str = Field(..., description="Task identifier")
    status: str = Field(..., description="Task status")
    progress: float = Field(0.0, ge=0.0, le=1.0, description="Progress (0.0 to 1.0)")
    result: Optional[SimulationResult] = Field(None, description="Result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Task creation time")
    started_at: Optional[datetime] = Field(None, description="Task start time")
    completed_at: Optional[datetime] = Field(None, description="Task completion time")

class ScenarioInfo(BaseModel):
    """Information about a scenario"""
    name: str = Field(..., description="Scenario name")
    description: str = Field("", description="Scenario description")
    type: str = Field("custom", description="Scenario type")
    parameters: Dict[str, Any] = Field({}, description="Scenario parameters")
    num_arrays: int = Field(0, description="Number of arrays")
    num_sources: int = Field(0, description="Number of sources")

class SystemSummary(BaseModel):
    """System summary information"""
    num_arrays: int = Field(0, description="Number of active arrays")
    num_sources: int = Field(0, description="Number of active sources")
    frequencies: List[float] = Field([], description="Active frequencies")
    grid_size: int = Field(200, description="Current grid size")
    grid_range: float = Field(10.0, description="Current grid range")
    beam_pattern_available: bool = Field(False, description="Whether beam pattern is available")
    interference_map_available: bool = Field(False, description="Whether interference map is available")

class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")