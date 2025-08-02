#!/usr/bin/env python3
"""
Run script for CK Empire Builder Backend
"""

import uvicorn
import logging
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main function to run the FastAPI application"""
    logger.info("🚀 Starting CK Empire Builder Backend...")
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main() 