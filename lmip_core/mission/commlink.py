import logging
import numpy as np

logger = logging.getLogger(__name__)

class CommLink:
    """
    Evaluates communication Line of Sight (LoS) from a rover on the lunar surface
    to a stationary lander or an orbital relay (simplified viewshed analysis).
    """
    
    def __init__(self, lander_height_m: float = 2.0, rover_antenna_height_m: float = 1.0):
        self.lander_height = lander_height_m
        self.rover_height = rover_antenna_height_m
        
    def check_line_of_sight(self, dem: np.ndarray, lander_pos: tuple, rover_pos: tuple) -> bool:
        """
        Performs a discrete ray-cast between lander and rover over the DEM.
        Returns True if Line of Sight is clear, False if obstructed by terrain.
        """
        y0, x0 = lander_pos
        y1, x1 = rover_pos
        
        # Bresenham's Line Algorithm (simplified for 2D grid ray-casting)
        points = self._get_line_points(x0, y0, x1, y1)
        
        if len(points) <= 2:
            return True # Too close to be obstructed
            
        # Extract elevations along the line
        elevations = np.array([dem[y, x] for x, y in points])
        
        # Add antenna heights to endpoints
        z_lander = elevations[0] + self.lander_height
        z_rover = elevations[-1] + self.rover_height
        
        # Calculate the direct line of sight vector in Z
        # z(t) = z_lander + t * (z_rover - z_lander) where t is from 0 to 1
        num_points = len(points)
        t_values = np.linspace(0, 1, num_points)
        los_z = z_lander + t_values * (z_rover - z_lander)
        
        # Check for terrain obstruction (excluding endpoints)
        for i in range(1, num_points - 1):
            if elevations[i] > los_z[i]:
                return False # Terrain blocks the signal
                
        return True
        
    def generate_viewshed_map(self, dem: np.ndarray, lander_pos: tuple) -> np.ndarray:
        """
        Generates a map where 1 = No Signal (obstructed), 0 = Signal (Clear LoS).
        This is computationally heavy, so in production we optimize or downsample.
        """
        logger.info(f"Generating viewshed comms map from lander at {lander_pos}...")
        rows, cols = dem.shape
        viewshed = np.zeros((rows, cols), dtype=int)
        
        # For simulation speed on a small grid, we iterate. 
        # For large grids, radial sweep algorithms are used.
        for y in range(rows):
            for x in range(cols):
                if not self.check_line_of_sight(dem, lander_pos, (y, x)):
                    viewshed[y, x] = 1 # Dead zone
                    
        return viewshed

    def _get_line_points(self, x0, y0, x1, y1):
        """Standard Bresenham's line algorithm."""
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = -1 if x0 > x1 else 1
        sy = -1 if y0 > y1 else 1
        
        if dx > dy:
            err = dx / 2.0
            while x != x1:
                points.append((x, y))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                points.append((x, y))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        points.append((x, y))
        return points
