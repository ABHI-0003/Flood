# API Handler

The API Handler component provides RESTful endpoints for the Flood Prediction System.

## Overview

This API serves as the communication layer between the web dashboard, database, and prediction models. It handles data retrieval, storage, and initiates flood risk predictions based on new sensor data.

## API Endpoints

### Health Check

```
GET /api/health
```

Returns the current status of the API server.

**Response:**
```json
{
  "status": "ok",
  "timestamp": 1635517890
}
```

### Get Raw Sensor Data

```
GET /api/raw
```

Returns the latest sensor readings.

**Response:**
```json
{
  "datetime": 1635517890,
  "temperature": 25.8,
  "relative_humidity": 80.5,
  "rain": 10.2,
  "surface_pressure": 1010.5,
  "soil_moisture": 0.75,
  "last_updated": "2023-04-15 14:30:45"
}
```

### Get Prediction Data

```
GET /api/prediction
```

Returns the latest flood risk predictions.

**Response:**
```json
{
  "datetime": 1635517890,
  "prediction_24": 1,
  "prediction_48": 2,
  "level_24": 1,
  "level_48": 2,
  "last_updated": "2023-04-15 14:30:45"
}
```

### Get Historical Data

```
GET /api/data/history?days=7
```

Returns historical sensor data for the specified number of days.

**Parameters:**
- `days` (optional): Number of days of history to retrieve (default: 7, max: 30)

**Response:**
```json
{
  "history": [
    {
      "datetime": 1635431490,
      "timestamp": "2023-04-14 14:30:45",
      "temperature": 24.5,
      "relative_humidity": 78.2,
      "rain": 5.1,
      "surface_pressure": 1009.8,
      "soil_moisture": 0.68
    },
    // Additional entries...
  ]
}
```

### Submit New Sensor Data

```
POST /api/newdata
```

Submit new sensor readings and trigger a prediction.

**Headers:**
- `Content-Type: application/json`
- `X-API-Key: <your-api-key>`

**Request Body:**
```json
{
  "temperature": 25.8,
  "humidity": 80.5,
  "rain": 10.2,
  "pressure": 1010.5,
  "soil_moisture": 0.75
}
```

**Response:**
```json
{
  "status": "Data updated successfully",
  "timestamp": 1635517890
}
```

## Authentication

The API uses a simple API key authentication scheme. Include your API key in the `X-API-Key` header for protected endpoints.

Example:
```
X-API-Key: a1b2c3d4e5f6g7h8i9j0
```

## Error Handling

All endpoints return appropriate HTTP status codes:
- 200: Successful request
- 400: Bad request (invalid parameters)
- 401: Unauthorized (invalid API key)
- 404: Endpoint not found
- 500: Server error

Error responses include a descriptive message:
```json
{
  "error": "Detailed error message"
}
```

## Running the API Server

Start the API server with:

```bash
python api_handler.py
```

Configuration via environment variables:
- `PORT`: Server port (default: 5000)
- `FLASK_ENV`: Set to "development" for debug mode

## Dependencies

- Flask
- Flask-CORS
- Python 3.8+