import logging
import numpy as np

logger = logging.getLogger(__name__)

class SolarSim:
    """
    Simulates solar illumination and permanent shadows on the lunar surface
    based on Digital Elevation Models (DEM) and solar angles.
    """
    
    def __init__(self, sun_azimuth_deg: float = 45.0, sun_elevation_deg: float = 10.0):
        self.sun_azimuth = np.radians(sun_azimuth_deg)
        self.sun_elevation = np.radians(sun_elevation_deg)
        
    def calculate_shadows(self, dem: np.ndarray, resolution_m: float = 1.0) -> np.ndarray:
        """
        Calculates a binary shadow map (1 = shadow, 0 = illuminated).
        Uses a simplified geometric ray-casting approach over the DEM.
        """
        logger.info("Calculating solar illumination and shadow masks...")
        
        # Calculate surface gradients
        dy, dx = np.gradient(dem, resolution_m, resolution_m)
        
        # Calculate slope and aspect (facing direction)
        slope = np.arctan(np.sqrt(dx**2 + dy**2))
        aspect = np.arctan2(dy, -dx)
        
        # Simple hillshade calculation (Lambertian reflectance)
        # Intensity = cos(solar_zenith)*cos(slope) + sin(solar_zenith)*sin(slope)*cos(solar_azimuth - aspect)
        solar_zenith = (np.pi / 2.0) - self.sun_elevation
        
        intensity = (np.cos(solar_zenith) * np.cos(slope)) + \
                    (np.sin(solar_zenith) * np.sin(slope) * np.cos(self.sun_azimuth - aspect))
                    
        # Areas where intensity is <= 0 are in self-shadow (facing away from sun steeper than elevation)
        # In a full simulation, we would also ray-cast to find cast shadows from distant peaks.
        shadow_map = np.zeros_like(dem, dtype=int)
        shadow_map[intensity <= 0] = 1
        
        # Add thermal penalty logic: permanent shadows drain battery due to heaters
        return shadow_map
        
    def get_thermal_penalty(self, shadow_map: np.ndarray, base_penalty: float = 5.0) -> np.ndarray:
        """
        Returns a cost multiplier array for pathfinding. Traversing shadows costs more energy.
        """
        penalty_map = np.ones_like(shadow_map, dtype=float)
        penalty_map[shadow_map == 1] = base_penalty
        return penalty_map
