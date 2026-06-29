import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from pathlib import Path
from lmip_core.polarfusion.ingestion import DataIngestor
from lmip_core.polarfusion.harmonization import DataHarmonizer

@patch('lmip_core.polarfusion.ingestion.rasterio.open')
def test_ingestor_load_geotiff(mock_open):
    # Mock rasterio open behavior
    mock_src = MagicMock()
    mock_src.meta = {'driver': 'GTiff', 'count': 1}
    mock_src.bounds = (0, 0, 10, 10)
    mock_src.crs.to_string.return_value = 'EPSG:4326'
    mock_src.width = 100
    mock_src.height = 100
    mock_src.count = 1
    mock_open.return_value.__enter__.return_value = mock_src
    
    # Needs to bypass path.exists() check for testing
    with patch('pathlib.Path.exists', return_value=True):
        ingestor = DataIngestor('/tmp/fake_dir')
        result = ingestor.load_dfsar('/tmp/fake_dir/fake_dfsar.tif')
        
        assert result['status'] == 'success'
        assert result['crs'] == 'EPSG:4326'
        assert result['type'] == 'DFSAR'
        assert result['width'] == 100

@patch('lmip_core.polarfusion.harmonization.rasterio.open')
@patch('lmip_core.polarfusion.harmonization.calculate_default_transform')
@patch('lmip_core.polarfusion.harmonization.reproject')
@patch('rasterio.band')
def test_harmonizer_reproject(mock_band, mock_reproject, mock_calc_transform, mock_open):
    # Mock calc transform
    mock_calc_transform.return_value = (MagicMock(), 200, 200)
    
    # Mock source and destination datasets
    mock_src = MagicMock(dtypes=('float32',), shape=(100, 100))
    mock_src.meta = {'driver': 'GTiff', 'count': 1}
    mock_src.count = 1
    mock_open.return_value.__enter__.return_value = mock_src
    
    harmonizer = DataHarmonizer(target_crs="EPSG:32761")
    
    with patch('pathlib.Path.exists', return_value=True):
        result = harmonizer.reproject_dataset('/tmp/src.tif', '/tmp/dst.tif')
        
        assert result['status'] == 'success'
        assert result['crs'] == 'EPSG:32761'
        assert result['width'] == 200
