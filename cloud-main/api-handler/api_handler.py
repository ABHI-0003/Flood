from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import sys
import os
import time
import json
import logging
import hashlib
from functools import wraps
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("api_handler")

# Import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../db-handler')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../predictor')))
import predictor
import dbhandler

app = Flask(__name__)
CORS(app)

# Simple API key authentication
API_KEYS = {
    "web_dashboard": "a1b2c3d4e5f6g7h8i9j0",
    "admin": "z9y8x7w6v5u4t3s2r1q0"
}

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip authentication for development environment
        if os.environ.get("FLASK_ENV") == "development":
            return f(*args, **kwargs)
            
        api_key = request.headers.get('X-API-Key')
        if api_key and api_key in API_KEYS.values():
            return f(*args, **kwargs)
        else:
            logger.warning(f"Unauthorized access attempt from {request.remote_addr}")
            return jsonify({"error": "Unauthorized: Invalid API key"}), 401
    return decorated_function

def get_raw_entry(n=1):
    try:
        database_handler = dbhandler.DatabaseHandler("../db-handler/dataset.db")
        last_entries = database_handler.get_last_entries("live_dataset", n)
        database_handler.close()
        
        if not last_entries:
            logger.warning("No entries found in database")
            return {"error": "No data available"}
            
        data = {}
        for entry in last_entries:
            data = {
                "datetime": entry[0],
                "temperature": round(float(entry[1]), 2),
                "relative_humidity": round(float(entry[2]), 2),
                "rain": round(float(entry[3]), 2),
                "surface_pressure": round(float(entry[4]), 2),
                "soil_moisture": round(float(entry[5]), 2),
                "last_updated": datetime.fromtimestamp(entry[0]).strftime('%Y-%m-%d %H:%M:%S')
            }
        return data
    except Exception as e:
        logger.error(f"Error retrieving raw data: {str(e)}")
        return {"error": str(e)}

def get_prediction_entry(n=1):
    try:
        database_handler = dbhandler.DatabaseHandler("../db-handler/dataset.db")
        last_entries = database_handler.get_last_entries("predictions", n)
        database_handler.close()
        
        if not last_entries:
            logger.warning("No prediction entries found in database")
            return {"error": "No prediction data available"}
            
        data = {}
        for entry in last_entries:
            data = {
                "datetime": entry[0],
                "prediction_24": int(entry[1]),
                "prediction_48": int(entry[2]),
                "level_24": int(entry[1]),  # For backward compatibility
                "level_48": int(entry[2]),  # For backward compatibility
                "last_updated": datetime.fromtimestamp(entry[0]).strftime('%Y-%m-%d %H:%M:%S')
            }
        return data
    except Exception as e:
        logger.error(f"Error retrieving prediction data: {str(e)}")
        return {"error": str(e)}

@app.before_request
def log_request():
    request_data = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "method": request.method,
        "path": request.path,
        "remote_addr": request.remote_addr,
        "user_agent": request.headers.get('User-Agent', ''),
        "api_key": request.headers.get('X-API-Key', '')[-4:] if request.headers.get('X-API-Key') else 'None'
    }
    logger.info(f"Request: {json.dumps(request_data)}")

@app.after_request
def log_response(response):
    response_data = {
        "status_code": response.status_code,
        "content_length": response.content_length
    }
    logger.info(f"Response: {json.dumps(response_data)}")
    return response

@app.route('/api/health')
def health_check():
    return jsonify({"status": "ok", "timestamp": time.time()})

@app.route('/api/raw')
@require_api_key
def raw():
    raw_data = get_raw_entry(1)
    if "error" in raw_data:
        return jsonify(raw_data), 500
    return jsonify(raw_data)

@app.route('/api/prediction')
@require_api_key
def prediction():
    prediction_data = get_prediction_entry(1)
    if "error" in prediction_data:
        return jsonify(prediction_data), 500
    return jsonify(prediction_data)

@app.route('/api/data/history', methods=['GET'])
@require_api_key
def history():
    try:
        days = request.args.get('days', default=7, type=int)
        if days < 1 or days > 30:
            return jsonify({"error": "Days parameter must be between 1 and 30"}), 400
            
        database_handler = dbhandler.DatabaseHandler("../db-handler/dataset.db")
        history_data = database_handler.get_last_entries("live_dataset", days * 24)  # Assuming hourly data
        database_handler.close()
        
        if not history_data:
            return jsonify({"error": "No historical data available"}), 404
            
        formatted_data = []
        for entry in history_data:
            formatted_data.append({
                "datetime": entry[0],
                "timestamp": datetime.fromtimestamp(entry[0]).strftime('%Y-%m-%d %H:%M:%S'),
                "temperature": float(entry[1]),
                "relative_humidity": float(entry[2]),
                "rain": float(entry[3]),
                "surface_pressure": float(entry[4]),
                "soil_moisture": float(entry[5])
            })
            
        return jsonify({"history": formatted_data})
    except Exception as e:
        logger.error(f"Error retrieving historical data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/newdata', methods=['POST'])
@require_api_key
def update_data():
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ["temperature", "humidity", "rain", "pressure", "soil_moisture"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
                
        # Validate data types
        for field in required_fields:
            try:
                data[field] = float(data[field])
            except (ValueError, TypeError):
                return jsonify({"error": f"Invalid value for {field}. Must be a number."}), 400
                
        # Process the data (store and predict)
        logger.info(f"Received new sensor data: {data}")
        
        # Run prediction model
        try:
            predictor.predict_flood(data)
            logger.info("Prediction completed successfully")
        except Exception as e:
            logger.error(f"Error in prediction: {str(e)}")
            # Continue processing even if prediction fails
        
        return jsonify({"status": "Data updated successfully", "timestamp": time.time()}), 200
    except Exception as e:
        logger.error(f"Error processing new data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    
    logger.info(f"Starting API server on port {port}, debug={debug}")
    app.run(host="0.0.0.0", port=port, debug=debug)
