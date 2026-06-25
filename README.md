# LunaNav AI — Explainable AI Mission Planning Platform for Lunar South Pole Exploration

LunaNav AI is an advanced, AI-driven mission planning platform designed to detect subsurface ice and optimize rover traversal in the permanently shadowed regions (PSRs) of the lunar South Pole. Built for the ISRO Chandrayaan-2 data hackathon, this project moves beyond simple rule-based heuristics to provide a robust, explainable, and multi-objective planning system.

## Project Vision

The discovery and characterization of water-ice in the lunar South Polar Region is a high-priority scientific objective for sustained human presence on the Moon. While traditional approaches rely on hardcoded thresholds (e.g., CPR > 1, DOP < 0.13), **LunaNav AI** fuses multi-modal data (DFSAR, OHRC, DEM) using machine learning to generate high-confidence ice probability maps, rank landing sites, and plan energy-aware rover traverses.

### Core Pipeline

1. **Preprocessing & Feature Fusion**: Ingests and aligns Chandrayaan-2 Dual Frequency Synthetic Aperture Radar (DFSAR) and Orbiter High Resolution Camera (OHRC) datasets.
2. **AI Ice Probability Mapping**: Fuses Radar Features, OHRC Texture, Slope, Roughness, and Shadow Duration into a predictive ML model for subsurface ice detection.
3. **Terrain Risk Assessment**: Evaluates crater morphology, boulder distribution, and surface roughness.
4. **Landing Site Ranking**: Ranks top landing sites based on a multi-objective scoring function (Safety, Distance to Ice, Illumination, Communication, Scientific Value).
5. **Energy-Aware Rover Path Planning**: An optimized path planner (advanced A*) factoring in slope, hazards, shadow duration, and battery consumption.
6. **Subsurface Ice Volume Estimation**: Utilizes radar backscatter models to estimate ice volume within the top 5 meters.
7. **Explainable AI (XAI)**: Provides confidence scores and reasoning for every ice detection (e.g., "Confidence 94% - High CPR, Low DOP, Persistent Shadow").
8. **Interactive Mission Dashboard**: A Streamlit application for visualization of probability heatmaps, landing sites, and rover routes.

## Proposed System Architecture

```text
lunanav-ai/
├── data/                  # Raw, processed, and cached datasets
├── models/                # ML models (ice_detector, terrain_classifier, etc.)
├── src/                   # Core Python modules
│   ├── preprocessing.py
│   ├── dfsar_processing.py
│   ├── feature_engineering.py
│   ├── ice_probability.py
│   ├── terrain_analysis.py
│   ├── landing_optimizer.py
│   ├── rover_navigation.py
│   ├── volume_estimation.py
│   ├── explainability.py
│   └── visualization.py
├── dashboard/             # Streamlit interactive dashboard
├── notebooks/             # Exploratory Data Analysis (EDA)
└── tests/                 # Scientific and engineering validation tests
```

## Datasets (Pending Finale Shortlist)
- Chandrayaan-2 Dual Frequency Synthetic Aperture Radar (DFSAR)
- Chandrayaan-2 Orbiter High Resolution Camera (OHRC)
- Lunar Digital Elevation Models (DEM)

## Tech Stack
- **Geospatial & Image Processing**: GDAL, rasterio, QGIS, ENVI
- **Data Science & ML**: Python, NumPy, SciPy, scikit-learn
- **Visualization & Dashboard**: Streamlit, Matplotlib

## Evaluation & Validation
Our approach will be rigorously evaluated against:
- **Scientific Validation**: Alignment of predicted ice regions with permanently shadowed areas and expected radar signatures.
- **Engineering Validation**: Ensuring rover paths avoid hazardous slopes and landing sites meet strict terrain constraints.
- **Performance Validation**: Efficient processing of crater datasets within operational timeframes.
