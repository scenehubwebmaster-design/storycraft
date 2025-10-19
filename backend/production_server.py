"""
Production server using Waitress WSGI server.
Waitress is a pure-Python production-quality WSGI server.
"""
from waitress import serve
from main import app
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Starting StoryCraft production server with Waitress...")
    logger.info("Server will be available at http://0.0.0.0:8000")
    
    # Serve the Flask app with Waitress
    # threads: number of worker threads (adjust based on your server)
    # channel_timeout: timeout for connections
    # max_request_header_size: 65536 (64KB) to handle larger headers
    serve(app, 
          host='0.0.0.0', 
          port=8000,
          threads=4,
          channel_timeout=120,
          max_request_header_size=65536,
          _quiet=False)
