FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose ports (will be overridden in docker-compose)
EXPOSE 8501

FROM base as worker
# Command to run the Temporal worker
CMD ["python", "run_worker.py"]

FROM base as dashboard
# Command to run the Streamlit dashboard
CMD ["streamlit", "run", "streamlit_app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]

# Default image (can run any component)
FROM base as default
CMD ["python", "--version"]
