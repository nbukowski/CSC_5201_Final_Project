#!/bin/bash

# Run the database population script
python populate_db.py

# Start the application
exec python app.py