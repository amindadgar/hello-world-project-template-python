# @@@SNIPSTART python-project-template-run-worker
import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker
import config

# Import workflows and activities
from workflows import HandleTelegramQuery, SayHello
from activities import (
    log_initial_request,
    invoke_llm,
    update_request_with_result,
    analyze_sentiment,
    handle_failure,
    say_hello
)

# Set up logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

async def main():
    """Main worker function"""
    
    # Connect to Temporal server
    tls_config = config.TLS_CONFIG if config.TLS_CONFIG else False
    
    client = await Client.connect(
        config.TEMPORAL_HOST,
        namespace=config.TEMPORAL_NAMESPACE,
        tls=tls_config
    )
    
    logger.info(f"Connected to Temporal server: {config.TEMPORAL_HOST}")
    logger.info(f"Namespace: {config.TEMPORAL_NAMESPACE}")
    logger.info(f"Task queue: {config.TASK_QUEUE}")
    
    # Create worker with workflows and activities
    worker = Worker(
        client,
        task_queue=config.TASK_QUEUE,
        workflows=[
            HandleTelegramQuery,  # Main AI agent workflow
            SayHello             # Legacy workflow for testing
        ],
        activities=[
            log_initial_request,
            invoke_llm,
            update_request_with_result,
            analyze_sentiment,
            handle_failure,
            say_hello            # Legacy activity for testing
        ],
    )
    
    logger.info("Worker registered with workflows and activities")
    logger.info("Starting worker...")
    
    # Run the worker
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
# @@@SNIPEND
