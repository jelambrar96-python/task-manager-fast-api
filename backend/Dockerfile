# Use the Python 3.12-slim base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install dependencies using Pipenv
RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy --ignore-pipfile

# Create a new user
# RUN groupadd appuser && useradd -m -s /bin/bash appuser

# Set the ownership of the application code to the new user
# RUN chown -R appuser:appuser /app

EXPOSE 8000

COPY . .

# Set the command to run the application as the new user
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]