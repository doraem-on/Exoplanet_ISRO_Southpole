import logging
import numpy as np
from typing import Tuple

logger = logging.getLogger(__name__)

class RoverKinematics:
    """
    Calculates actual Watt-hour (Wh) energy consumption for lunar rovers
    based on terrain slope, distance, gravity, and rover mass.
    """
    
    def __init__(self, mass_kg: float = 27.0, velocity_ms: float = 0.01):
        self.mass = mass_kg
        self.velocity = velocity_ms
        self.gravity = 1.62 # m/s^2 (Lunar gravity)
        self.rolling_resistance_coeff = 0.05 # Typical for soft lunar regolith
        self.motor_efficiency = 0.6 # 60% efficiency
        
    def calculate_step_energy_wh(self, distance_m: float, slope_deg: float) -> float:
        """
        Calculates the Watt-hours consumed traversing a specific distance over a given slope.
        """
        slope_rad = np.radians(slope_deg)
        
        # 1. Rolling Resistance Force
        # Fr = C_rr * N = C_rr * m * g * cos(theta)
        f_rolling = self.rolling_resistance_coeff * self.mass * self.gravity * np.cos(slope_rad)
        
        # 2. Grade Resistance Force (gravity pulling down the slope)
        # Fg = m * g * sin(theta)
        f_grade = self.mass * self.gravity * np.sin(slope_rad)
        
        # Total Force required to move at constant velocity
        f_total = f_rolling + f_grade
        
        # If moving downhill, regenerative braking might happen, but usually we just assume low power.
        # For simplicity, we clip force to a minimum idle power requirement.
        if f_total < 0:
            f_total = 0.1 * f_rolling # Idle power or braking power
            
        # Energy (Joules) = Work = Force * distance
        energy_joules = (f_total * distance_m) / self.motor_efficiency
        
        # Convert Joules to Watt-hours (1 Wh = 3600 J)
        energy_wh = energy_joules / 3600.0
        
        # Add basic housekeeping power (electronics, sensors) over the time taken
        time_seconds = distance_m / self.velocity
        housekeeping_power_w = 10.0 # Watts
        housekeeping_energy_wh = (housekeeping_power_w * time_seconds) / 3600.0
        
        return energy_wh + housekeeping_energy_wh
