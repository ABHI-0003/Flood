import numpy as np
import pandas as pd
import joblib
import os
import sys
import logging
from tensorflow.keras.models import load_model
from typing import Dict, Any, Union, List, Tuple
import time
import json
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("predictor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("predictor")

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../db-handler')))
import dbhandler

# Define constants
MODEL_24H_PATH = "../predictor/flood_prediction_24h.keras"
MODEL_48H_PATH = "../predictor/flood_prediction_48h.keras"
SCALER_PATH = "../predictor/scaler.pkl"
DB_PATH = "../db-handler/dataset.db"

class FloodPredictor:
    """
    Flood prediction system using machine learning models.
    
    This class loads trained Keras models to predict flood risk levels
    based on environmental sensor data.
    """
    
    def __init__(self):
        """Initialize the predictor by loading models and connecting to the database."""
        try:
            logger.info("Initializing Flood Predictor")
            
            # Load models
            self._load_models()
            
            # Connect to database
            self.database_handler = dbhandler.DatabaseHandler(DB_PATH)
            
            logger.info("Flood Predictor initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Flood Predictor: {str(e)}")
            raise
            
    def _load_models(self):
        """Load the ML models and scaler."""
        try:
            logger.info("Loading prediction models and scaler")
            
            # Check if model files exist
            for path in [MODEL_24H_PATH, MODEL_48H_PATH, SCALER_PATH]:
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Required file not found: {path}")
            
            # Load models
            self.model_24 = load_model(MODEL_24H_PATH)
            self.model_48 = load_model(MODEL_48H_PATH)
            
            # Load scaler
            self.scaler = joblib.load(SCALER_PATH)
            
            logger.info("Models and scaler loaded successfully")
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
    
    def predict(self, data: Dict[str, float]) -> Dict[str, Any]:
        """
        Make flood risk predictions based on current sensor data.
        
        Args:
            data: Dictionary containing sensor readings with keys:
                - temperature: Air temperature in Celsius
                - humidity: Relative humidity as percentage
                - rain: Rainfall amount in mm
                - pressure: Surface pressure in hPa
                - soil_moisture: Soil moisture level in m
                
        Returns:
            Dictionary containing prediction results
        """
        try:
            logger.info(f"Making prediction with data: {data}")
            
            # Validate input data
            self._validate_input(data)
            
            # Get previous data for time series
            prev_data = self.database_handler.get_last_entries("live_dataset", 29)
            
            if len(prev_data) < 29:
                logger.warning(f"Insufficient historical data. Only {len(prev_data)} entries found, 29 required.")
                # Could implement fallback logic here
            
            # Convert to DataFrame
            prev_data = pd.DataFrame([entry[1:] for entry in prev_data])
            
            # Create new data point
            new_sensor_df = pd.DataFrame([[
                data["temperature"], 
                data["humidity"], 
                data["rain"], 
                data["pressure"], 
                data["soil_moisture"]
            ]])
            
            # Update database with new reading
            self.database_handler.update_dataset(
                "live_dataset", 
                (
                    data["temperature"], 
                    data["humidity"], 
                    data["rain"],
                    data["pressure"], 
                    data["soil_moisture"]
                )
            )
            
            # Combine previous and new data
            rolling_data = pd.concat([prev_data, new_sensor_df], ignore_index=True).tail(30)
            logger.debug(f"Combined data shape: {rolling_data.shape}")
            
            # Scale the data
            scaled_input = self.scaler.transform(rolling_data)
            
            # Reshape for LSTM input (1 sample, 30 timesteps, 5 features)
            lstm_input = scaled_input.reshape(1, 30, 5)
            
            # Make predictions
            prediction_24 = self.model_24.predict(lstm_input)
            prediction_48 = self.model_48.predict(lstm_input)
            
            # Get risk levels (0=low, 1=medium, 2=high)
            level_24 = int(np.argmax(prediction_24))
            level_48 = int(np.argmax(prediction_48))
            
            # Update prediction database
            self.database_handler.update_predictions("predictions", (level_24, level_48))
            
            # Prepare result
            result = {
                "timestamp": int(time.time()),
                "datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "24h_risk": level_24,
                "24h_probabilities": prediction_24[0].tolist(),
                "48h_risk": level_48,
                "48h_probabilities": prediction_48[0].tolist(),
                "risk_map": {
                    "0": "Low Risk (Below 50%)",
                    "1": "Medium Risk (75% - 90%)",
                    "2": "High Risk (Above 90%)"
                }
            }
            
            logger.info(f"Prediction completed. 24h risk: {level_24}, 48h risk: {level_48}")
            return result
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise
            
    def _validate_input(self, data: Dict[str, float]):
        """
        Validate input data format and values.
        
        Args:
            data: Dictionary of sensor readings
            
        Raises:
            ValueError: If data is invalid
        """
        required_fields = ["temperature", "humidity", "rain", "pressure", "soil_moisture"]
        
        # Check all required fields are present
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Check values are numeric
        for field in required_fields:
            try:
                data[field] = float(data[field])
            except (ValueError, TypeError):
                raise ValueError(f"Invalid value for {field}. Must be a number.")
        
        # Check values are in reasonable ranges
        validators = {
            "temperature": lambda x: -40 <= x <= 60,
            "humidity": lambda x: 0 <= x <= 100,
            "rain": lambda x: 0 <= x <= 2000,
            "pressure": lambda x: 800 <= x <= 1200,
            "soil_moisture": lambda x: 0 <= x <= 100
        }
        
        for field, validator in validators.items():
            if not validator(data[field]):
                logger.warning(f"Unusual value for {field}: {data[field]}")


def predict_flood(data: Dict[str, float]) -> Dict[str, Any]:
    """
    Make flood predictions based on current sensor data.
    Wrapper function for the FloodPredictor class.
    
    Args:
        data: Dictionary of sensor readings
        
    Returns:
        Dictionary containing prediction results
    """
    try:
        predictor = FloodPredictor()
        return predictor.predict(data)
    except Exception as e:
        logger.error(f"Error in predict_flood: {str(e)}")
        # Return error dictionary
        return {
            "error": str(e),
            "timestamp": int(time.time()),
            "status": "error"
        }


# If script is run directly, make a test prediction
if __name__ == "__main__":
    test_data = {
        "temperature": 25.8,
        "humidity": 80.5,
        "rain": 10.2,
        "pressure": 1010.5,
        "soil_moisture": 0.75
    }
    
    # Run prediction
    result = predict_flood(test_data)
    
    # Pretty print result
    print(json.dumps(result, indent=2))