from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class FTComponent(str, Enum):
    MAGNITUDE = "magnitude"
    PHASE = "phase"
    REAL = "real"
    IMAGINARY = "imaginary"
    MAGNITUDE_LOG = "magnitude_log"

class RegionType(str, Enum):
    INNER = "inner"
    OUTER = "outer"

class ImageUploadRequest(BaseModel):
    image_id: str = Field(..., description="Unique identifier for the image")
    position: int = Field(..., ge=0, le=3, description="Position (0-3) for the image")

class Rectangle(BaseModel):
    x: int = Field(..., description="X coordinate of rectangle center")
    y: int = Field(..., description="Y coordinate of rectangle center")
    width: int = Field(..., description="Width of rectangle")
    height: int = Field(..., description="Height of rectangle")

class MixRequest(BaseModel):
    image_ids: List[str] = Field(..., min_items=1, max_items=4, description="List of image IDs to mix")
    weights: List[float] = Field(..., min_items=1, max_items=4, description="Weights for each image")
    output_position: int = Field(0, ge=0, le=1, description="Output viewport (0 or 1)")
    mix_type: str = Field("magnitude_phase", description="Type of mixing (magnitude_phase or real_imaginary)")

class RegionFilterRequest(BaseModel):
    image_ids: List[str] = Field(..., min_items=1, max_items=4, description="List of image IDs to filter")
    rectangle: Rectangle = Field(..., description="Rectangle region")
    region_type: RegionType = Field(RegionType.INNER, description="Inner or outer region")
    apply_to_all: bool = Field(True, description="Apply to all images")

class BrightnessContrastRequest(BaseModel):
    image_id: str = Field(..., description="Image ID to adjust")
    brightness: float = Field(0.0, ge=-1.0, le=1.0, description="Brightness adjustment (-1 to 1)")
    contrast: float = Field(1.0, ge=0.1, le=3.0, description="Contrast adjustment (0.1 to 3)")
    component: Optional[FTComponent] = Field(None, description="Specific component to adjust")

class FTResponse(BaseModel):
    image_id: str
    original_path: str
    ft_components: Dict[str, str]  # Base64 encoded images
    image_shape: List[int]
    status: str = "success"

class MixResponse(BaseModel):
    task_id: str
    output_path: str
    progress: float = 0.0
    estimated_time: Optional[float] = None
    status: str = "processing"