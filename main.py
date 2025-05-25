#!/usr/bin/env python3
"""
Main entry point for the AI Health Tracker API
This file is used for deployment platforms like Render, Heroku, etc.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the FastAPI app from the backend
from app.main import app

# Export the app for uvicorn
__all__ = ['app']

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000))) 