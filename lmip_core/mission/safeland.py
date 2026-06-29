import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

class SafeLand:
    """
    Identifies and ranks optimal landing sites based on terrain safety,
    scientific value (ice confidence), and accessibility.
    """
    
    def __init__(self, max_slope_deg: float = 15.0, min_ice_confidence: float = 0.6):
        self.max_slope_deg = max_slope_deg
        self.min_ice_confidence = min_ice_confidence
        
    def evaluate_hazards(self, slope_map: np.ndarray, roughness_map: np.ndarray) -> np.ndarray:
        """
        Generates a binary hazard map where 1 is hazardous (unsafe) and 0 is safe.
        """
        logger.info("Evaluating terrain hazards for landing sites...")
        # Simple heuristic: hazardous if slope > max_slope or roughness is very high
        hazard_map = np.zeros_like(slope_map, dtype=int)
        hazard_map[slope_map > self.max_slope_deg] = 1
        
        # In a real implementation, roughness thresholds would depend on lander specs.
        # Assuming roughness map is normalized 0-1, thresholding at 0.8
        hazard_map[roughness_map > 0.8] = 1
        
        return hazard_map
        
    def rank_landing_sites(self, ice_confidence_map: np.ndarray, hazard_map: np.ndarray, num_sites: int = 5, min_distance: float = 10.0) -> List[Dict]:
        """
        Ranks top landing sites avoiding hazards and maximizing ice confidence.
        
        Returns a list of dictionaries with coordinates and scores.
        """
        logger.info("Ranking landing sites based on science and safety...")
        
        # Mask out hazardous areas (set their confidence to -1)
        safe_confidence = np.copy(ice_confidence_map)
        safe_confidence[hazard_map == 1] = -1.0
        
        # Also mask out areas below minimum ice confidence
        safe_confidence[safe_confidence < self.min_ice_confidence] = -1.0
        
        # Find top N candidate pixels
        flat_indices = np.argsort(safe_confidence.ravel())[::-1]
        
        ranked_sites = []
        for idx in flat_indices:
            if safe_confidence.ravel()[idx] == -1.0:
                break # No more valid safe sites
                
            y, x = np.unravel_index(idx, safe_confidence.shape)
            
            # Simple heuristic: Avoid picking sites right next to each other
            # In a real system, we'd use a clustering algorithm (e.g., DBSCAN) 
            # to find distinct landing zones.
            is_distinct = True
            for site in ranked_sites:
                dist = np.sqrt((site['x'] - x)**2 + (site['y'] - y)**2)
                if dist < min_distance:  # Minimum pixel distance between ranked sites
                    is_distinct = False
                    break
                    
            if is_distinct:
                ranked_sites.append({
                    "rank": len(ranked_sites) + 1,
                    "x": int(x),
                    "y": int(y),
                    "ice_confidence": float(ice_confidence_map[y, x]),
                    "score": float(safe_confidence[y, x])
                })
                
            if len(ranked_sites) >= num_sites:
                break
                
        logger.info(f"Identified {len(ranked_sites)} valid landing sites.")
        return ranked_sites
