# Dockerfile for Wellnessapp (main API)
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the Poetry lock files and project file
COPY pyproject.toml poetry.lock /app/

# Install Poetry and dependencies
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the rest of the application code
COPY . /app

# Run the FastAPI app
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
