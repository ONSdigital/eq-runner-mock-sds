# Use the official Python 3.11 image as the base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV HTTP_KEEP_ALIVE 650

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc

# Set the working directory in the container
WORKDIR /app

# Copy only the necessary files for poetry installation
COPY pyproject.toml poetry.lock /app/

# Install Poetry
RUN pip install poetry==1.5.1

# Install the application dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy the rest of the application code
COPY . /app

# Expose the port that Gunicorn will listen on
EXPOSE 5003

# Start Gunicorn to serve the application
CMD ["gunicorn", "app.main:app", "-b", "0.0.0.0:5003", "--worker-class", "uvicorn.workers.UvicornWorker", "--timeout", "0"]
