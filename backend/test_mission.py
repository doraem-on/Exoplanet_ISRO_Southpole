import pytest
import numpy as np
from lmip_core.mission.safeland import SafeLand
from lmip_core.mission.traverseiq import TraverseIQ

def test_safeland_evaluate_hazards():
    sl = SafeLand(max_slope_deg=15.0)
    
    # 5x5 maps
    slope = np.zeros((5, 5))
    slope[0, 0] = 20.0 # Hazard
    
    roughness = np.zeros((5, 5))
    roughness[4, 4] = 0.9 # Hazard
    
    hazards = sl.evaluate_hazards(slope, roughness)
    
    assert hazards[0, 0] == 1
    assert hazards[4, 4] == 1
    assert hazards[2, 2] == 0
    assert hazards.sum() == 2

def test_safeland_rank_sites():
    sl = SafeLand(min_ice_confidence=0.5)
    
    ice = np.zeros((10, 10))
    ice[2, 2] = 0.9
    ice[8, 8] = 0.8
    ice[1, 1] = 0.4 # Below threshold
    
    hazards = np.zeros((10, 10))
    
    ranked = sl.rank_landing_sites(ice, hazards, num_sites=2, min_distance=2.0)
    
    assert len(ranked) == 2
    assert ranked[0]['ice_confidence'] == 0.9
    assert ranked[0]['x'] == 2 and ranked[0]['y'] == 2
    assert ranked[1]['ice_confidence'] == 0.8
    
def test_traverseiq_plan_path():
    tiq = TraverseIQ()
    
    # 5x5 grid
    hazards = np.zeros((5, 5))
    slope = np.zeros((5, 5))
    
    # Block middle row except last column
    hazards[2, 0:4] = 1
    
    start = (0, 0)
    goal = (4, 0)
    
    path = tiq.plan_path(start, goal, hazards, slope)
    
    assert path is not None
    assert path[0] == start
    assert path[-1] == goal
    
    # Ensure path avoids hazards
    for (y, x) in path:
        assert hazards[y, x] == 0
