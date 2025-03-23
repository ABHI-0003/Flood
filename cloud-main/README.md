# Flood Prediction System

A comprehensive system for predicting flood risks using machine learning models, environmental sensors, and a web-based dashboard.

## Project Overview

This project consists of several interconnected components:

1. **Website**: A user-friendly web interface for viewing flood predictions and sensor data
2. **API Handler**: RESTful API endpoints for data exchange between components
3. **Database Handler**: Manages data storage and retrieval
4. **Predictor**: Machine learning models that process sensor data to predict flood risks

## System Architecture

```
+----------------+     +----------------+     +----------------+
|                |     |                |     |                |
|   Web Browser  |<--->|  API Handler   |<--->|  DB Handler    |
|                |     |                |     |                |
+----------------+     +----------------+     +----------------+
                                ^
                                |
                                v
                       +----------------+
                       |                |
                       |   Predictor    |
                       |                |
                       +----------------+
```

## Installation

### Prerequisites

- Python 3.8+
- Node.js 14+ (for website development)
- SQLite3
- TensorFlow 2.x

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/flood-prediction.git
   cd flood-prediction
   ```

2. Install dependencies for each component:
   ```bash
   # Install predictor dependencies
   cd predictor
   pip install -r requirements.txt
   
   # Install API handler dependencies
   cd ../api-handler
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   cd ../db-handler
   python -c "import dbhandler; dbhandler.DatabaseHandler('dataset.db')"
   ```

4. Start the API server:
   ```bash
   cd ../api-handler
   python api_handler.py
   ```

5. Serve the website:
   ```bash
   cd ../website
   # Use any HTTP server, for example:
   python -m http.server 8000
   ```

6. Access the dashboard at http://localhost:8000

## Component Details

### Website

The website provides a user interface for visualizing flood predictions and sensor data. It includes:

- Home page with project information
- Dashboard with real-time predictions and sensor readings
- Interactive charts for data visualization

### API Handler

The API handler provides endpoints for data exchange:

- `/api/raw` - Get latest sensor readings
- `/api/prediction` - Get latest flood predictions
- `/api/newdata` - Update with new sensor data

### Database Handler

Manages SQLite database operations:

- Store sensor readings
- Store prediction results
- Retrieve historical data

### Predictor

Machine learning component that processes sensor data:

- Takes sensor readings as input
- Uses trained LSTM models
- Outputs 24-hour and 48-hour flood risk predictions

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
