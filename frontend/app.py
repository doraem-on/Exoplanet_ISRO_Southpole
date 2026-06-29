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

if st.sidebar.button("🚀 Run Mission Simulation", type="primary"):
    with st.spinner("Executing Mission AI Pipeline (PolarFusion -> IceSense -> SafeLand -> TraverseIQ)..."):
        try:
            response = requests.post(f"{BACKEND_URL}/run-mission", json={
                "grid_size": grid_size,
                "start_x": start_x,
                "start_y": start_y
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
    slope_map = np.array(data['slope_map'])
    sites = data['landing_sites']
    path = data['traverse_path']
    
    tab1, tab2, tab3 = st.tabs(["🗺️ Lunar Digital Twin", "🔬 Scientific Analysis", "📊 Mission Analytics"])
    
    with tab1:
        st.markdown("### Digital Twin: Terrain & Traversal")
        
        # Plotly Heatmap for Ice Confidence
        fig = go.Figure(data=go.Heatmap(
            z=ice_map,
            colorscale='Blues',
            name='Ice Confidence',
            colorbar=dict(title='Ice Prob')
        ))
        
        # Add Hazards
        hazard_y, hazard_x = np.where(hazard_map == 1)
        fig.add_trace(go.Scatter(
            x=hazard_x, y=hazard_y,
            mode='markers',
            marker=dict(color='rgba(255, 0, 0, 0.4)', size=4, symbol='square'),
            name='Hazards'
        ))
        
        # Add Landing Sites
        if sites:
            site_x = [s['x'] for s in sites]
            site_y = [s['y'] for s in sites]
            texts = [f"Rank {s['rank']} (Conf: {s['ice_confidence']:.2f})" for s in sites]
            fig.add_trace(go.Scatter(
                x=site_x, y=site_y,
                mode='markers+text',
                marker=dict(color='gold', size=12, symbol='star'),
                text=texts,
                textposition="top center",
                name='Ranked Sites'
            ))
            
        # Add Traverse Path
        if path:
            path_x = [p['x'] for p in path]
            path_y = [p['y'] for p in path]
            fig.add_trace(go.Scatter(
                x=path_x, y=path_y,
                mode='lines+markers',
                line=dict(color='green', width=3),
                marker=dict(size=4),
                name='Rover Path'
            ))
            
        fig.update_layout(
            height=600, 
            width=800,
            title="South Pole Candidate Crater",
            xaxis_title="X (m)", yaxis_title="Y (m)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        st.markdown("### IceSense AI Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Max Ice Confidence", f"{ice_map.max():.2f}")
            st.markdown("**Ice Probability Distribution**")
            # Simple histogram using Plotly
            hist_fig = go.Figure(data=[go.Histogram(x=ice_map.ravel(), nbinsx=20)])
            st.plotly_chart(hist_fig, use_container_width=True)
            
        with col2:
            st.metric("Hazard Ratio", f"{(hazard_map.sum() / hazard_map.size * 100):.1f}%")
            st.markdown("**SafeLand Recommended Zones**")
            if sites:
                df_sites = pd.DataFrame(sites)
                st.dataframe(df_sites.style.highlight_max(subset=['score']))
            else:
                st.warning("No safe landing sites found!")
                
    with tab3:
        st.markdown("### Mission Readiness Score")
        
        if not sites or not path:
            st.error("MISSION ABORT: Unsafe terrain or inaccessible target.")
        else:
            path_length = len(path)
            avg_ice = np.mean([s['ice_confidence'] for s in sites])
            score = (avg_ice * 100) - (path_length * 0.5)
            
            st.metric(
                label="Mission Score (0-100)", 
                value=f"{max(0, min(100, score)):.1f}", 
                delta="GO for Launch" if score > 50 else "NO GO"
            )
            
            st.markdown("#### Traverse Summary")
            st.write(f"- **Steps to Target:** {path_length}")
            st.write(f"- **Target Coordinates:** ({path[-1]['x']}, {path[-1]['y']})")
else:
    st.info("👈 Please set mission parameters and click 'Run Mission Simulation'.")
