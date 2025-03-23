import sqlite3
import os
import time
import logging
from contextlib import contextmanager
from typing import List, Tuple, Any, Optional, Dict, Union

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("database.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("dbhandler")

class DatabaseHandler:
    def __init__(self, db_name: str):
        """Initialize database connection.
        
        Args:
            db_name: Path to the SQLite database file
        """
        self.db_name = db_name
        
        if not os.path.exists(db_name):
            logger.error(f"Database {db_name} does not exist.")
            self._initialize_database()
        
        self.connection = None
        self._connect()
    
    def _connect(self):
        """Establish database connection."""
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_name}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def _initialize_database(self):
        """Create a new database with required tables if it doesn't exist."""
        try:
            logger.info(f"Creating new database: {self.db_name}")
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS live_dataset (
                datetime INTEGER PRIMARY KEY,
                temperature REAL,
                relative_humidity REAL,
                rain REAL,
                surface_pressure REAL,
                soil_moisture REAL
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                datetime INTEGER PRIMARY KEY,
                prediction_24 INTEGER,
                prediction_48 INTEGER
            )
            ''')
            
            # Create indexes for faster queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_live_dataset_datetime ON live_dataset(datetime)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_datetime ON predictions(datetime)')
            
            conn.commit()
            conn.close()
            logger.info("Database tables created successfully")
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
            raise

    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor.
        
        Yields:
            sqlite3.Cursor: Database cursor
        """
        if self.connection is None:
            self._connect()
            
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()

    def execute_query(self, query: str, params: tuple = ()):
        """Execute an SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
            return True
        except sqlite3.Error as e:
            logger.error(f"Query execution error: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            return False

    def get_last_entries(self, table_name: str, n: int = 1) -> List[Tuple]:
        """Get the last n entries from a table.
        
        Args:
            table_name: Name of the database table
            n: Number of entries to retrieve
            
        Returns:
            List of database rows as tuples
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table_name} ORDER BY datetime DESC LIMIT {n}")
                results = cursor.fetchall()
                return [tuple(row) for row in results][::-1]
        except sqlite3.Error as e:
            logger.error(f"Error fetching data: {e}")
            return []
    
    def update_dataset(self, table_name: str, data: tuple):
        """Insert a new sensor data record.
        
        Args:
            table_name: Name of the database table
            data: Tuple of sensor data (temperature, humidity, rain, pressure, soil_moisture)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Updating dataset: {data}")
            query = f"""
            INSERT INTO {table_name} 
            (datetime, temperature, relative_humidity, rain, surface_pressure, soil_moisture) 
            VALUES (?, ?, ?, ?, ?, ?)
            """
            return self.execute_query(query, (int(time.time()), *data))
        except Exception as e:
            logger.error(f"Error updating dataset: {e}")
            return False
        
    def update_predictions(self, table_name: str, predictions: tuple):
        """Insert a new prediction record.
        
        Args:
            table_name: Name of the database table
            predictions: Tuple of prediction values (prediction_24, prediction_48)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Updating predictions: {predictions}")
            query = f"""
            INSERT INTO {table_name} 
            (datetime, prediction_24, prediction_48) 
            VALUES (?, ?, ?)
            """
            return self.execute_query(query, (int(time.time()), *predictions))
        except Exception as e:
            logger.error(f"Error updating predictions: {e}")
            return False
            
    def get_data_between_dates(self, table_name: str, start_time: int, end_time: int) -> List[Dict]:
        """Get data within a specified time range.
        
        Args:
            table_name: Name of the database table
            start_time: Start timestamp (Unix time)
            end_time: End timestamp (Unix time)
            
        Returns:
            List of data records as dictionaries
        """
        try:
            with self.get_cursor() as cursor:
                query = f"SELECT * FROM {table_name} WHERE datetime BETWEEN ? AND ? ORDER BY datetime"
                cursor.execute(query, (start_time, end_time))
                columns = [column[0] for column in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching data between dates: {e}")
            return []

    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database.
        
        Args:
            backup_path: Path to save the backup
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import shutil
            shutil.copy2(self.db_name, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Database backup error: {e}")
            return False

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed.")
        else:
            logger.warning("No database connection to close.")
    
    def __del__(self):
        """Destructor to ensure connection is closed properly."""
        self.close()