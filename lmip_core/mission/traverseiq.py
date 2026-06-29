import logging
import numpy as np
import heapq
import itertools
from typing import List, Tuple, Optional, Dict
from .rover_kinematics import RoverKinematics

logger = logging.getLogger(__name__)

class TraverseIQ:
    """
    Optimizes rover traverse paths from a landing site to multiple scientific targets 
    while minimizing energy (Watt-hours) and avoiding terrain/communication hazards.
    """
    
    def __init__(self):
        self.kinematics = RoverKinematics()
        
    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int], resolution_m: float = 1.0) -> float:
        """Euclidean distance heuristic for A* in meters, converted to an optimistic energy cost."""
        dist = np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2) * resolution_m
        # Optimistic energy: traversing flat ground at idle power
        return self.kinematics.calculate_step_energy_wh(dist, 0.0)
        
    def plan_path(self, 
                  start: Tuple[int, int], 
                  goal: Tuple[int, int], 
                  hazard_map: np.ndarray, 
                  slope_map: np.ndarray,
                  shadow_penalty_map: np.ndarray = None,
                  comms_deadzone_map: np.ndarray = None,
                  resolution_m: float = 1.0) -> Tuple[Optional[List[Tuple[int, int]]], float]:
        """
        Uses A* Search to find the optimal path considering physics and constraints.
        Returns (path, total_energy_wh).
        """
        if hazard_map[start[0], start[1]] == 1:
            return None, 0.0
        if hazard_map[goal[0], goal[1]] == 1:
            return None, 0.0
            
        rows, cols = hazard_map.shape
        open_set = []
        heapq.heappush(open_set, (0.0, 0.0, start))
        
        came_from = {}
        cost_so_far = {start: 0.0}
        
        neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0), 
                     (1, 1), (-1, -1), (1, -1), (-1, 1)]
                     
        while open_set:
            _, current_energy, current = heapq.heappop(open_set)
            
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path, current_energy
                
            for dy, dx in neighbors:
                ny, nx = current[0] + dy, current[1] + dx
                next_node = (ny, nx)
                
                if 0 <= ny < rows and 0 <= nx < cols:
                    # Obstacle checks
                    if hazard_map[ny, nx] == 1:
                        continue
                    if comms_deadzone_map is not None and comms_deadzone_map[ny, nx] == 1:
                        continue # Strict constraint: avoid comms loss
                        
                    # Calculate physics-based step energy
                    step_distance = np.sqrt(dy**2 + dx**2) * resolution_m
                    step_slope = slope_map[ny, nx]
                    
                    energy_cost = self.kinematics.calculate_step_energy_wh(step_distance, step_slope)
                    
                    # Apply thermal penalty if in shadow
                    if shadow_penalty_map is not None:
                        energy_cost *= shadow_penalty_map[ny, nx]
                    
                    new_energy = current_energy + energy_cost
                    
                    if next_node not in cost_so_far or new_energy < cost_so_far[next_node]:
                        cost_so_far[next_node] = new_energy
                        priority = new_energy + self._heuristic(goal, next_node, resolution_m)
                        heapq.heappush(open_set, (priority, new_energy, next_node))
                        came_from[next_node] = current
                        
        return None, 0.0

    def solve_tsp(self, start: Tuple[int, int], targets: List[Tuple[int, int]], 
                  hazard_map: np.ndarray, slope_map: np.ndarray, 
                  shadow_penalty: np.ndarray = None, comms_map: np.ndarray = None) -> Dict:
        """
        Finds the optimal visitation sequence for multiple targets (TSP) using permutations.
        Returns the combined path and total energy.
        """
        logger.info(f"Solving TSP for {len(targets)} scientific targets...")
        
        # Precompute pairwise paths and costs between all nodes (start + targets)
        nodes = [start] + targets
        n_nodes = len(nodes)
        
        cost_matrix = np.full((n_nodes, n_nodes), np.inf)
        path_matrix = [[None for _ in range(n_nodes)] for _ in range(n_nodes)]
        
        for i in range(n_nodes):
            for j in range(n_nodes):
                if i == j:
                    cost_matrix[i][j] = 0.0
                else:
                    path, cost = self.plan_path(nodes[i], nodes[j], hazard_map, slope_map, shadow_penalty, comms_map)
                    if path:
                        cost_matrix[i][j] = cost
                        path_matrix[i][j] = path
                        
        # Evaluate all permutations of visiting targets
        best_cost = np.inf
        best_order = None
        
        target_indices = list(range(1, n_nodes))
        for perm in itertools.permutations(target_indices):
            # Route: Start -> perm[0] -> perm[1] ...
            current_cost = 0.0
            current_node = 0 # Start node index
            valid = True
            
            for next_node in perm:
                edge_cost = cost_matrix[current_node][next_node]
                if edge_cost == np.inf:
                    valid = False
                    break
                current_cost += edge_cost
                current_node = next_node
                
            if valid and current_cost < best_cost:
                best_cost = current_cost
                best_order = perm
                
        if best_order is None:
            logger.warning("No valid route exists to visit all targets.")
            return {"path": [], "energy_wh": 0.0, "order": []}
            
        # Reconstruct full path
        full_path = []
        current_node = 0
        for next_node in best_order:
            segment = path_matrix[current_node][next_node]
            if not full_path:
                full_path.extend(segment)
            else:
                # Avoid duplicating the waypoint coordinate
                full_path.extend(segment[1:])
            current_node = next_node
            
        ordered_targets = [nodes[i] for i in best_order]
        logger.info(f"Optimal multi-target route found. Total Energy: {best_cost:.2f} Wh")
        
        return {
            "path": full_path,
            "energy_wh": best_cost,
            "order": ordered_targets
        }
