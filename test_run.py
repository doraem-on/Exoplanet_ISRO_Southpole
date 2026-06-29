import traceback
from backend.main import run_mission, MissionRequest

req = MissionRequest(grid_size=20, start_x=0, start_y=0, sun_elevation=10.0, lander_x=0, lander_y=0)

try:
    resp = run_mission(req)
    print("Success")
except Exception as e:
    traceback.print_exc()
