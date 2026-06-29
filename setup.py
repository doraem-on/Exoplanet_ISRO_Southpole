from setuptools import setup, find_packages

setup(
    name="lmip_core",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "rasterio",
        "geopandas",
        "shapely",
        "scikit-learn",
        "xgboost",
        "shap"
    ],
    description="Core library for Lunar Mission Intelligence Platform",
)
