from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import logging

from lmip_core.mission.safeland import SafeLand
from lmip_core.mission.traverseiq import TraverseIQ
from lmip_core.mission.solarsim import SolarSim
from lmip_core.mission.commlink import CommLink

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
    sun_elevation: float = 10.0
    lander_x: int = 0
    lander_y: int = 0

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
    shadow_map: list
    comms_map: list
    landing_sites: list[LandingSite]
    traverse_path: list[Point]
    total_energy_wh: float
    target_order: list[Point]

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "LMIP Backend is running"}

@app.post("/run-mission", response_model=MissionResponse)
def run_mission(req: MissionRequest):
    """
    Simulates a full mission pipeline execution.
    Generates synthetic terrain, predicts ice, evaluates physics constraints, 
    finds multiple landing sites, and plots a multi-target TSP traverse path.
    """
    try:
        size = req.grid_size
        
        # 1. Simulate Terrain & Ice
        slope_map = np.random.uniform(0, 30, (size, size))
        roughness_map = np.random.uniform(0, 1, (size, size))
        
        ice_confidence_map = np.zeros((size, size))
        center = size // 2
        y, x = np.ogrid[-center:size-center, -center:size-center]
        mask = x**2 + y**2 <= (size//4)**2
        ice_confidence_map[mask] = np.random.uniform(0.7, 1.0, np.sum(mask))
        ice_confidence_map += np.random.uniform(0, 0.2, (size, size))
        ice_confidence_map = np.clip(ice_confidence_map, 0, 1)

        # Generate a simulated DEM (Digital Elevation Model)
        # Higher in the corners, deep crater in the middle
        dem = np.zeros((size, size))
        for i in range(size):
            for j in range(size):
                dem[i, j] = ((i - center)**2 + (j - center)**2) * 0.1
        
        # 2. Physics Constraints (Phase 6)
        solarsim = SolarSim(sun_elevation_deg=req.sun_elevation)
        shadow_map = solarsim.calculate_shadows(dem)
        shadow_penalty = solarsim.get_thermal_penalty(shadow_map)
        
        commlink = CommLink()
        comms_map = commlink.generate_viewshed_map(dem, (req.lander_y, req.lander_x))

        # 3. SafeLand
        safeland = SafeLand(max_slope_deg=15.0, min_ice_confidence=0.6)
        hazard_map = safeland.evaluate_hazards(slope_map, roughness_map)
        
        landing_sites = safeland.rank_landing_sites(
            ice_confidence_map, 
            hazard_map, 
            num_sites=3,
            min_distance=5.0
        )
        
        # 4. TraverseIQ Multi-Target (Phase 7)
        traverseiq = TraverseIQ()
        start_pt = (req.start_y, req.start_x)
        
        targets = []
        for site in landing_sites:
            targets.append((site['y'], site['x']))
            
        path_points = []
        target_order = []
        total_energy = 0.0
        
        if targets:
            result = traverseiq.solve_tsp(
                start=start_pt, 
                targets=targets, 
                hazard_map=hazard_map, 
                slope_map=slope_map,
                shadow_penalty=shadow_penalty,
                comms_map=comms_map
            )
            
            path = result.get('path', [])
            total_energy = result.get('energy_wh', 0.0)
            order = result.get('order', [])
            
            if path:
                logger.info(f"Generated path: {path}")
                path_points = [{"y": p[0], "x": p[1]} for p in path]
                target_order = [{"y": p[0], "x": p[1]} for p in order]
                
        return MissionResponse(
            ice_map=ice_confidence_map.tolist(),
            hazard_map=hazard_map.tolist(),
            slope_map=slope_map.tolist(),
            shadow_map=shadow_map.tolist(),
            comms_map=comms_map.tolist(),
            landing_sites=[LandingSite(**site) for site in landing_sites],
            traverse_path=[Point(**p) for p in path_points],
            total_energy_wh=total_energy,
            target_order=[Point(**p) for p in target_order]
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.exception("Mission failed with exception:")
        raise HTTPException(status_code=500, detail=str(e))
