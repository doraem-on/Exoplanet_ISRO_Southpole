from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import logging

from lmip_core.mission.safeland import SafeLand
from lmip_core.mission.traverseiq import TraverseIQ

app = FastAPI(
    title="LMIP Backend API",
    description="Backend API for the Lunar Mission Intelligence Platform",
    version="1.0.0"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MissionRequest(BaseModel):
    grid_size: int = 50
    start_x: int = 0
    start_y: int = 0

class Point(BaseModel):
    x: int
    y: int

class LandingSite(BaseModel):
    rank: int
    x: int
    y: int
    ice_confidence: float
    score: float

class MissionResponse(BaseModel):
    ice_map: list
    hazard_map: list
    slope_map: list
    landing_sites: list[LandingSite]
    traverse_path: list[Point]

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "LMIP Backend is running"}

@app.post("/run-mission", response_model=MissionResponse)
def run_mission(req: MissionRequest):
    """
    Simulates a full mission pipeline execution.
    Generates synthetic terrain, predicts ice, finds landing sites, and plots a traverse path.
    """
    try:
        size = req.grid_size
        
        # 1. Simulate Terrain & Ice (Phase 2 & 3 Output Mock)
        # In a real system, these would be the output of `FeatureEngineer` and `IceConfidenceModel`
        slope_map = np.random.uniform(0, 30, (size, size)) # 0 to 30 degrees
        roughness_map = np.random.uniform(0, 1, (size, size))
        
        # Create a "crater" of high ice confidence in the middle
        ice_confidence_map = np.zeros((size, size))
        center = size // 2
        y, x = np.ogrid[-center:size-center, -center:size-center]
        mask = x**2 + y**2 <= (size//4)**2
        ice_confidence_map[mask] = np.random.uniform(0.7, 1.0, np.sum(mask))
        
        # Add some random noise
        ice_confidence_map += np.random.uniform(0, 0.2, (size, size))
        ice_confidence_map = np.clip(ice_confidence_map, 0, 1)

        # 2. Run SafeLand
        safeland = SafeLand(max_slope_deg=15.0, min_ice_confidence=0.6)
        hazard_map = safeland.evaluate_hazards(slope_map, roughness_map)
        
        landing_sites = safeland.rank_landing_sites(
            ice_confidence_map, 
            hazard_map, 
            num_sites=3,
            min_distance=5.0
        )
        
        # 3. Run TraverseIQ
        traverseiq = TraverseIQ()
        
        # Start from user defined point (or 0,0)
        start_pt = (req.start_y, req.start_x)
        
        # Target the top ranked landing site if available
        path_points = []
        if landing_sites:
            target_pt = (landing_sites[0]['y'], landing_sites[0]['x'])
            path = traverseiq.plan_path(start_pt, target_pt, hazard_map, slope_map)
            
            if path:
                path_points = [{"y": p[0], "x": p[1]} for p in path]
                
        return MissionResponse(
            ice_map=ice_confidence_map.tolist(),
            hazard_map=hazard_map.tolist(),
            slope_map=slope_map.tolist(),
            landing_sites=[LandingSite(**site) for site in landing_sites],
            traverse_path=[Point(**p) for p in path_points]
        )
        
    except Exception as e:
        logger.error(f"Mission failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
