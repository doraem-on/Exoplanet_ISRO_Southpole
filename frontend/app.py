import streamlit as st
import requests
import numpy as np
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="LMIP Mission Dashboard",
    page_icon="🌕",
    layout="wide",
)

st.title("🌕 Lunar Mission Intelligence Platform (LMIP)")
st.subheader("AI-Assisted Decision Support System for Autonomous Lunar Polar Exploration")
st.markdown("---")

BACKEND_URL = "http://backend:8000"

# Sidebar Controls
st.sidebar.header("Mission Parameters")
grid_size = st.sidebar.slider("Grid Size (px)", min_value=20, max_value=100, value=50, step=10)
start_x = st.sidebar.number_input("Lander Drop X", min_value=0, max_value=grid_size-1, value=0)
start_y = st.sidebar.number_input("Lander Drop Y", min_value=0, max_value=grid_size-1, value=0)
sun_elev = st.sidebar.slider("Sun Elevation (deg)", min_value=1.0, max_value=30.0, value=10.0, step=1.0)

# Render Controls
st.sidebar.header("3D Overlay Controls")
show_shadows = st.sidebar.checkbox("Show Permanent Shadows", value=True)
show_comms = st.sidebar.checkbox("Show Comms Deadzones", value=False)
show_hazards = st.sidebar.checkbox("Show Steep Hazards", value=True)

if st.sidebar.button("🚀 Run Mission Simulation", type="primary"):
    with st.spinner("Executing Mission AI Pipeline (Physics -> IceSense -> SafeLand -> TSP TraverseIQ)..."):
        try:
            response = requests.post(f"{BACKEND_URL}/run-mission", json={
                "grid_size": grid_size,
                "start_x": start_x,
                "start_y": start_y,
                "sun_elevation": sun_elev,
                "lander_x": start_x,
                "lander_y": start_y
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                st.session_state['mission_data'] = data
                st.success("Mission pipeline executed successfully!")
            else:
                st.error(f"Mission failed: {response.text}")
        except Exception as e:
            st.error(f"Connection error: {e}")

# Main Dashboard
if 'mission_data' in st.session_state:
    data = st.session_state['mission_data']
    
    ice_map = np.array(data['ice_map'])
    hazard_map = np.array(data['hazard_map'])
    shadow_map = np.array(data['shadow_map'])
    comms_map = np.array(data['comms_map'])
    sites = data['landing_sites']
    path = data['traverse_path']
    target_order = data['target_order']
    total_energy = data['total_energy_wh']
    
    # Generate a matching DEM purely for 3D visualization to match backend
    center = grid_size // 2
    y, x = np.mgrid[0:grid_size, 0:grid_size]
    dem = ((x - center)**2 + (y - center)**2) * 0.1
    
    tab1, tab2, tab3 = st.tabs(["🌍 3D Digital Twin", "🔬 Advanced Physics & Science", "📊 Mission Telemetry"])
    
    with tab1:
        st.markdown("### 3D Lunar Digital Twin")
        
        # Base 3D Surface (Ice Confidence mapped to colors)
        fig = go.Figure(data=[go.Surface(
            z=dem,
            surfacecolor=ice_map,
            colorscale='Blues',
            colorbar=dict(title='Ice Prob', x=-0.1),
            name='Terrain & Ice'
        )])
        
        # Overlays
        # For Plotly 3D, we can overlay scatter3d points
        
        if show_shadows:
            sy, sx = np.where(shadow_map == 1)
            sz = dem[sy, sx] + 0.5
            fig.add_trace(go.Scatter3d(
                x=sx, y=sy, z=sz,
                mode='markers',
                marker=dict(size=2, color='black', opacity=0.5),
                name='Shadows'
            ))
            
        if show_comms:
            cy, cx = np.where(comms_map == 1)
            cz = dem[cy, cx] + 0.5
            fig.add_trace(go.Scatter3d(
                x=cx, y=cy, z=cz,
                mode='markers',
                marker=dict(size=2, color='orange', opacity=0.5),
                name='No Signal'
            ))
            
        if show_hazards:
            hy, hx = np.where(hazard_map == 1)
            hz = dem[hy, hx] + 0.5
            fig.add_trace(go.Scatter3d(
                x=hx, y=hy, z=hz,
                mode='markers',
                marker=dict(size=3, color='red', symbol='square', opacity=0.6),
                name='Hazards'
            ))
        
        # Add Landing Sites
        if sites:
            site_x = [s['x'] for s in sites]
            site_y = [s['y'] for s in sites]
            site_z = [dem[s['y'], s['x']] + 2 for s in sites]
            texts = [f"Rank {s['rank']}" for s in sites]
            
            fig.add_trace(go.Scatter3d(
                x=site_x, y=site_y, z=site_z,
                mode='markers+text',
                marker=dict(color='gold', size=8, symbol='diamond'),
                text=texts,
                textposition="top center",
                name='Science Targets'
            ))
            
        # Add Traverse Path
        if path:
            path_x = [p['x'] for p in path]
            path_y = [p['y'] for p in path]
            path_z = [dem[p['y'], p['x']] + 1 for p in path]
            
            fig.add_trace(go.Scatter3d(
                x=path_x, y=path_y, z=path_z,
                mode='lines',
                line=dict(color='lime', width=4),
                name='Rover Path (TSP)'
            ))
            
        fig.update_layout(
            height=700,
            scene=dict(
                xaxis_title="X (m)",
                yaxis_title="Y (m)",
                zaxis_title="Elevation (m)",
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=0.3)
            ),
            margin=dict(l=0, r=0, b=0, t=30)
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        st.markdown("### Physics Constraints")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Shadow Coverage", f"{(shadow_map.sum() / shadow_map.size * 100):.1f}%")
            st.metric("Sun Elevation", f"{sun_elev}°")
            st.markdown("**SafeLand Recommended Zones**")
            if sites:
                df_sites = pd.DataFrame(sites)
                st.dataframe(df_sites.style.highlight_max(subset=['score']))
                
        with col2:
            st.metric("Signal Deadzones", f"{(comms_map.sum() / comms_map.size * 100):.1f}%")
            st.metric("Steep Hazards", f"{(hazard_map.sum() / hazard_map.size * 100):.1f}%")
                
    with tab3:
        st.markdown("### Rover Telemetry & Multi-Target Plan")
        
        if not sites or not path:
            st.error("MISSION ABORT: Unsafe terrain, inaccessible targets, or no valid TSP route.")
        else:
            avg_ice = np.mean([s['ice_confidence'] for s in sites])
            score = (avg_ice * 100) - (total_energy * 0.1)
            
            col1, col2 = st.columns(2)
            col1.metric(
                label="Mission Score (0-100)", 
                value=f"{max(0, min(100, score)):.1f}", 
                delta="GO for Launch" if score > 50 else "NO GO"
            )
            col2.metric(
                label="Total Energy Required",
                value=f"{total_energy:.2f} Wh",
                delta="Nominal" if total_energy < 500 else "High Drain",
                delta_color="inverse"
            )
            
            st.markdown("#### Autonomous Visitation Sequence (TSP)")
            st.write(f"1. **Start:** Lander Drop Point ({start_x}, {start_y})")
            for i, target in enumerate(target_order):
                st.write(f"{i+2}. **Target:** ({target['x']}, {target['y']})")
                
else:
    st.info("👈 Set mission constraints in the sidebar and deploy!")
