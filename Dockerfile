# Use the official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install netcat-openbsd for checking database availability and necessary build tools
RUN apt-get update && apt-get install -y netcat-openbsd gcc libmariadb-dev-compat libmariadb-dev && apt-get clean

# Install Gunicorn
RUN pip install gunicorn

# Copy the wait-for-it script
COPY wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# Ensure entrypoint.sh is executable
RUN chmod +x /app/entrypoint.sh

# Expose the port the app runs on
EXPOSE 5005

# Run the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
