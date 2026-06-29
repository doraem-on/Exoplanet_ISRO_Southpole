import logging
from pathlib import Path
from typing import Dict, Any, Union, Optional
import rasterio

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestor:
    """
    Handles the ingestion of raw satellite imagery and DEM files.
    """
    
    def __init__(self, data_dir: Union[str, Path]):
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            logger.warning(f"Data directory {self.data_dir} does not exist. Creating it.")
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
    def _load_geotiff(self, filepath: Union[str, Path], source_type: str) -> Dict[str, Any]:
        """Generic method to load metadata from a GeoTIFF."""
        filepath = Path(filepath)
        if not filepath.exists():
            logger.error(f"{source_type} file not found: {filepath}")
            raise FileNotFoundError(f"{source_type} file not found: {filepath}")
            
        try:
            with rasterio.open(filepath) as src:
                metadata = src.meta.copy()
                bounds = src.bounds
                crs = src.crs.to_string() if src.crs else "UNKNOWN"
                
                logger.info(f"Successfully loaded {source_type} from {filepath}. CRS: {crs}, Shape: {src.shape}")
                
                return {
                    "type": source_type,
                    "path": str(filepath),
                    "metadata": metadata,
                    "bounds": bounds,
                    "crs": crs,
                    "width": src.width,
                    "height": src.height,
                    "count": src.count, # number of bands
                    "status": "success"
                }
        except Exception as e:
            logger.error(f"Failed to read {source_type} file {filepath}: {e}")
            raise
            
    def load_dfsar(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """Loads Dual-Frequency Synthetic Aperture Radar (DFSAR) data."""
        return self._load_geotiff(filepath, "DFSAR")
        
    def load_ohrc(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """Loads Orbiter High Resolution Camera (OHRC) data."""
        return self._load_geotiff(filepath, "OHRC")
        
    def load_dem(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """Loads Digital Elevation Model (DEM) data."""
        return self._load_geotiff(filepath, "DEM")
