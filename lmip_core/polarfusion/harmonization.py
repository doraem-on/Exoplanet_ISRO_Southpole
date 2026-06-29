import logging
from typing import Dict, Any, Union, Optional
from pathlib import Path
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

logger = logging.getLogger(__name__)

class DataHarmonizer:
    """
    Harmonizes multiple data sources (DFSAR, OHRC, DEM) by aligning them 
    to a common coordinate reference system (CRS) and resolution.
    """
    
    def __init__(self, target_crs: str = "EPSG:32761"): # South Pole Stereographic
        self.target_crs = target_crs
        
    def reproject_dataset(self, source_path: Union[str, Path], dest_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Reprojects a single raster dataset to the target CRS.
        """
        source_path = Path(source_path)
        dest_path = Path(dest_path)
        
        logger.info(f"Reprojecting {source_path} to {self.target_crs}")
        
        try:
            with rasterio.open(source_path) as src:
                transform, width, height = calculate_default_transform(
                    src.crs, self.target_crs, src.width, src.height, *src.bounds
                )
                
                kwargs = src.meta.copy()
                kwargs.update({
                    'crs': self.target_crs,
                    'transform': transform,
                    'width': width,
                    'height': height
                })
                
                # Ensure destination directory exists
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                with rasterio.open(dest_path, 'w', **kwargs) as dst:
                    for i in range(1, src.count + 1):
                        reproject(
                            source=rasterio.band(src, i),
                            destination=rasterio.band(dst, i),
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=transform,
                            dst_crs=self.target_crs,
                            resampling=Resampling.bilinear
                        )
            
            return {
                "status": "success",
                "source": str(source_path),
                "reprojected_path": str(dest_path),
                "crs": self.target_crs,
                "width": width,
                "height": height
            }
            
        except Exception as e:
            logger.error(f"Reprojection failed for {source_path}: {e}")
            raise
            
    def align_datasets(self, dfsar_data: Dict, ohrc_data: Dict, dem_data: Dict, output_dir: Union[str, Path]) -> Dict[str, Any]:
        """
        Aligns the input datasets to the target CRS and spatial resolution.
        """
        logger.info(f"Harmonizing datasets to CRS: {self.target_crs}")
        output_dir = Path(output_dir)
        
        results = {}
        
        for name, data in [("dfsar", dfsar_data), ("ohrc", ohrc_data), ("dem", dem_data)]:
            if data and data.get("path"):
                out_path = output_dir / f"{name}_aligned.tif"
                try:
                    res = self.reproject_dataset(data["path"], out_path)
                    results[name] = res
                except Exception as e:
                    results[name] = {"status": "error", "error": str(e)}
        
        return {
            "status": "success",
            "crs": self.target_crs,
            "results": results
        }
