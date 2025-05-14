import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Temporal configuration
TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost:7233")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")
TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "hello-task-queue")

# Optional TLS configuration
TEMPORAL_TLS_CERT = os.getenv("TEMPORAL_TLS_CERT")
TEMPORAL_TLS_KEY = os.getenv("TEMPORAL_TLS_KEY")
TEMPORAL_TLS_CA = os.getenv("TEMPORAL_TLS_CA")

# TLS configuration if certificates are provided
TLS_CONFIG = None
if all([TEMPORAL_TLS_CERT, TEMPORAL_TLS_KEY, TEMPORAL_TLS_CA]):
    TLS_CONFIG = {
        "client_cert": TEMPORAL_TLS_CERT,
        "client_private_key": TEMPORAL_TLS_KEY,
        "server_root_ca_cert": TEMPORAL_TLS_CA,
    } 