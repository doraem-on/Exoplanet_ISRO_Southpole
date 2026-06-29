import logging
import numpy as np
import heapq
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

class TraverseIQ:
    """
    Optimizes rover traverse paths from a landing site to scientific targets 
    while minimizing energy and avoiding terrain hazards.
    """
    
    def __init__(self):
        pass
        
    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Euclidean distance heuristic for A*."""
        return np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
        
    def plan_path(self, 
                  start: Tuple[int, int], 
                  goal: Tuple[int, int], 
                  hazard_map: np.ndarray, 
                  slope_map: np.ndarray) -> Optional[List[Tuple[int, int]]]:
        """
        Uses A* Search to find the optimal path.
        
        Args:
            start: (y, x) starting coordinate.
            goal: (y, x) goal coordinate.
            hazard_map: 2D array where 1 is an obstacle.
            slope_map: 2D array indicating terrain slope (used as a cost penalty).
            
        Returns:
            List of (y, x) coordinates representing the path, or None if no path found.
        """
        logger.info(f"Planning traverse path from {start} to {goal}...")
        
        if hazard_map[start[0], start[1]] == 1:
            logger.error("Start point is inside a hazard!")
            return None
            
        if hazard_map[goal[0], goal[1]] == 1:
            logger.error("Goal point is inside a hazard!")
            return None
            
        rows, cols = hazard_map.shape
        
        # Priority queue: stores (cost + heuristic, cost, (y, x))
        open_set = []
        heapq.heappush(open_set, (0.0, 0.0, start))
        
        came_from = {}
        cost_so_far = {start: 0.0}
        
        # 8-connected grid directions
        neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0), 
                     (1, 1), (-1, -1), (1, -1), (-1, 1)]
                     
        while open_set:
            _, current_cost, current = heapq.heappop(open_set)
            
            if current == goal:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                logger.info(f"Path found with {len(path)} steps.")
                return path
                
            for dy, dx in neighbors:
                ny, nx = current[0] + dy, current[1] + dx
                next_node = (ny, nx)
                
                # Bounds check
                if 0 <= ny < rows and 0 <= nx < cols:
                    # Obstacle check
                    if hazard_map[ny, nx] == 1:
                        continue
                        
                    # Calculate step cost. Diagonal moves cost more (sqrt(2)).
                    # Add penalty for slope to simulate energy expenditure.
                    step_distance = np.sqrt(dy**2 + dx**2)
                    slope_penalty = slope_map[ny, nx] * 0.1 # Weight parameter
                    new_cost = current_cost + step_distance + slope_penalty
                    
                    if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                        cost_so_far[next_node] = new_cost
                        priority = new_cost + self._heuristic(goal, next_node)
                        heapq.heappush(open_set, (priority, new_cost, next_node))
                        came_from[next_node] = current
                        
        logger.warning("No valid path found to the goal.")
        return None
