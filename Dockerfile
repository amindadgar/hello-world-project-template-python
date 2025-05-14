FROM python:3.11-slim as base

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

FROM base as worker
# Command to run the worker
CMD ["python", "run_worker.py"] 

# We don't have the concept of server here
# But this is just for testing the workflow
FROM base as server
# Command to run the server
CMD ["python", "run_workflow.py"]
