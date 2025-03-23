# Database Handler

The Database Handler component manages data storage and retrieval for the Flood Prediction System.

## Overview

This module provides a clean interface for interacting with the SQLite database that stores sensor readings and prediction results.

## Database Schema

### Live Dataset Table

Stores environmental sensor readings:

| Column | Type | Description |
|--------|------|-------------|
| datetime | INTEGER | Unix timestamp (primary key) |
| temperature | REAL | Temperature in Celsius |
| relative_humidity | REAL | Humidity percentage |
| rain | REAL | Rainfall in mm |
| surface_pressure | REAL | Air pressure in hPa |
| soil_moisture | REAL | Soil moisture level in m |

### Predictions Table

Stores flood risk prediction results:

| Column | Type | Description |
|--------|------|-------------|
| datetime | INTEGER | Unix timestamp (primary key) |
| prediction_24 | INTEGER | 24-hour prediction (0=low, 1=medium, 2=high) |
| prediction_48 | INTEGER | 48-hour prediction (0=low, 1=medium, 2=high) |

## Usage

### Initialization

```python
from dbhandler import DatabaseHandler

# Initialize with database path
db = DatabaseHandler("../db-handler/dataset.db")
```

### Retrieving Data

```python
# Get the last 10 sensor readings
sensor_data = db.get_last_entries("live_dataset", 10)

# Get the most recent prediction
prediction = db.get_last_entries("predictions", 1)

# Get data between specific dates
start_time = 1635431490  # Unix timestamp
end_time = 1635517890    # Unix timestamp
historical_data = db.get_data_between_dates("live_dataset", start_time, end_time)
```

### Updating Data

```python
# Add new sensor reading
# (temperature, humidity, rain, pressure, soil_moisture)
db.update_dataset("live_dataset", (25.8, 80.5, 10.2, 1010.5, 0.75))

# Add new prediction
# (prediction_24, prediction_48)
db.update_predictions("predictions", (1, 2))
```

### Database Management

```python
# Create database backup
db.backup_database("backup/dataset_backup.db")

# Close connection properly
db.close()
```

## Error Handling

The DatabaseHandler handles SQLite errors gracefully and provides detailed logging. All database operations are wrapped in try-except blocks to prevent crashes.

## Database Initialization

If the database doesn't exist, the handler will automatically create it with the required schema.

## Implementation Details

- Uses SQLite for lightweight, file-based database storage
- Implements connection pooling for efficient connection management
- Provides context managers for safe transaction handling
- Includes comprehensive logging for debugging and monitoring

## Dependencies

- Python 3.6+
- SQLite3 (built into Python)
