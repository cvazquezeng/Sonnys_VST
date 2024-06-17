#!/bin/bash
# wait-for-it.sh script ensures the MySQL server is available before proceeding
./wait-for-it.sh db:3306 --timeout=60 --strict -- echo "MySQL is up"

# Initialize the database
python initialize_db.py

# Start the application using Gunicorn
exec gunicorn -b 0.0.0.0:5005 run:app
