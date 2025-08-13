"""
Script to wait for database to be available.
Used in Docker entrypoint to ensure database is ready before running migrations.
"""

import time
import psycopg2
import os
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Max number of retries
MAX_RETRIES = 30
# Delay between retries (seconds)
RETRY_DELAY = 2


def wait_for_database(database_url=None):
    """
    Wait for database to be available.
    
    Args:
        database_url (str): Database URL string. If None, uses DATABASE_URL env var.
    
    Returns:
        bool: True if database is available, False otherwise.
    """
    if not database_url:
        database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        logger.error("No DATABASE_URL provided")
        return False
    
    # Parse database URL
    url = urlparse(database_url)
    dbname = url.path[1:]  # Remove leading slash
    user = url.username
    password = url.password
    host = url.hostname
    port = url.port
    
    logger.info(f"Waiting for database connection to {host}:{port}...")
    
    for i in range(MAX_RETRIES):
        try:
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port,
                connect_timeout=3,
            )
            conn.close()
            logger.info("Database is available!")
            return True
        except psycopg2.OperationalError as e:
            logger.warning(f"Database not yet available (attempt {i+1}/{MAX_RETRIES}): {e}")
            time.sleep(RETRY_DELAY)
    
    logger.error(f"Could not connect to database after {MAX_RETRIES} attempts")
    return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = wait_for_database()
    exit(0 if success else 1) 