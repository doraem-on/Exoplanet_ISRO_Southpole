import requests
import json
try:
    resp = requests.post("http://localhost:8000/run-mission", json={"grid_size": 20, "start_x": 0, "start_y": 0, "sun_elevation": 10.0, "lander_x": 0, "lander_y": 0})
    print(resp.text)
except Exception as e:
    print(e)
