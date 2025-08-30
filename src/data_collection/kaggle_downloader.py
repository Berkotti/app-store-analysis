"""
Kaggle dataset downloader for App Store data
Created: 2025-08-29
Updated: 2025-08-29
"""

import os
import sys
import zipfile
from pathlib import Path
from typing import List, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import (
    KAGGLE_USERNAME,
    KAGGLE_KEY,
    KAGGLE_DATASETS,
    RAW_DATA_DIR
)
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger("kaggle_downloader")


class KaggleDownloader:
    """Download and extract Kaggle datasets"""
    
    def __init__(self):
        """Initialize Kaggle downloader"""
        self.setup_kaggle_credentials()
        self.data_dir = RAW_DATA_DIR / "kaggle"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def setup_kaggle_credentials(self):
        """Set up Kaggle API credentials"""
        if KAGGLE_USERNAME and KAGGLE_KEY:
            os.environ['KAGGLE_USERNAME'] = KAGGLE_USERNAME
            os.environ['KAGGLE_KEY'] = KAGGLE_KEY
            logger.info("Kaggle credentials set from environment")
        else:
            # Check if kaggle.json exists
            kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
            if not kaggle_json.exists():
                logger.warning(
                    "No Kaggle credentials found. Please set up your Kaggle API:\n"
                    "1. Go to https://www.kaggle.com/account\n"
                    "2. Create New API Token\n"
                    "3. Place kaggle.json in ~/.kaggle/ or set env variables"
                )
                return False
        return True
    
    def download_dataset(self, dataset_name: str) -> bool:
        """
        Download a single Kaggle dataset
        
        Args:
            dataset_name: Kaggle dataset identifier (e.g., 'user/dataset-name')
        
        Returns:
            Success status
        """
        try:
            import kaggle
            
            dataset_dir = self.data_dir / dataset_name.replace("/", "_")
            dataset_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Downloading dataset: {dataset_name}")
            kaggle.api.dataset_download_files(
                dataset_name,
                path=dataset_dir,
                unzip=True
            )
            
            logger.info(f"Dataset downloaded successfully: {dataset_name}")
            return True
            
        except ImportError:
            logger.error("Kaggle package not installed. Run: pip install kaggle")
            return False
        except Exception as e:
            logger.error(f"Error downloading {dataset_name}: {str(e)}")
            return False
    
    def download_all_datasets(self, datasets: Optional[List[str]] = None) -> dict:
        """
        Download multiple Kaggle datasets
        
        Args:
            datasets: List of dataset identifiers (uses config default if None)
        
        Returns:
            Dictionary with download status for each dataset
        """
        if datasets is None:
            datasets = KAGGLE_DATASETS
        
        results = {}
        for dataset in datasets:
            success = self.download_dataset(dataset)
            results[dataset] = success
            
        # Summary
        successful = sum(1 for v in results.values() if v)
        logger.info(f"Downloaded {successful}/{len(datasets)} datasets successfully")
        
        return results
    
    def list_downloaded_files(self) -> List[Path]:
        """List all downloaded files in the Kaggle data directory"""
        files = []
        for file_path in self.data_dir.rglob("*"):
            if file_path.is_file():
                files.append(file_path)
                logger.debug(f"Found file: {file_path}")
        
        logger.info(f"Total files found: {len(files)}")
        return files
    
    def get_dataset_info(self, dataset_name: str) -> dict:
        """
        Get information about a downloaded dataset
        
        Args:
            dataset_name: Kaggle dataset identifier
        
        Returns:
            Dictionary with dataset information
        """
        dataset_dir = self.data_dir / dataset_name.replace("/", "_")
        
        if not dataset_dir.exists():
            logger.warning(f"Dataset directory not found: {dataset_dir}")
            return {}
        
        info = {
            "name": dataset_name,
            "path": str(dataset_dir),
            "files": [],
            "total_size": 0
        }
        
        for file_path in dataset_dir.rglob("*"):
            if file_path.is_file():
                size = file_path.stat().st_size
                info["files"].append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": size
                })
                info["total_size"] += size
        
        info["total_size_mb"] = round(info["total_size"] / (1024 * 1024), 2)
        logger.info(f"Dataset {dataset_name}: {len(info['files'])} files, {info['total_size_mb']} MB")
        
        return info


def main():
    """Main function to download Kaggle datasets"""
    downloader = KaggleDownloader()
    
    # Check if credentials are set up
    if not downloader.setup_kaggle_credentials():
        logger.error("Please set up Kaggle credentials first")
        return
    
    # Download all configured datasets
    logger.info("Starting dataset downloads...")
    results = downloader.download_all_datasets()
    
    # List downloaded files
    logger.info("\nListing downloaded files...")
    files = downloader.list_downloaded_files()
    
    # Get info for each dataset
    logger.info("\nDataset information:")
    for dataset in KAGGLE_DATASETS:
        info = downloader.get_dataset_info(dataset)
        if info:
            print(f"\n{dataset}:")
            print(f"  Files: {len(info['files'])}")
            print(f"  Size: {info['total_size_mb']} MB")
            for file_info in info['files'][:5]:  # Show first 5 files
                print(f"    - {file_info['name']}")


if __name__ == "__main__":
    main()