# Use the Python 3.12-slim base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the Pipfile and Pipfile.lock
COPY  requirements.txt .

# Install dependencies using pip
RUN pip install -r requirements.txt --no-cache-dir

# Create a new user if it doesn't already exist
RUN getent group appuser || groupadd appuser && useradd -m -g appuser -s /bin/bash appuser

# Set the ownership of the application code to the new user
RUN chown -R appuser:appuser /app

EXPOSE 8000

COPY . .

# Set the command to run the application as the new user
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
