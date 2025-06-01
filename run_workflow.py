# @@@SNIPSTART python-project-template-run-workflow-hello-world
import asyncio
import logging
import uuid
from datetime import datetime
from temporalio.client import Client
from workflows import HandleTelegramQuery, SayHello
from models import TelegramRequestInput, WorkflowResult
import config

# Set up logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

async def run_hello_world():
    """Run the legacy hello world workflow for testing"""
    
    # Connect to Temporal server
    tls_config = config.TLS_CONFIG if config.TLS_CONFIG else False
    
    client = await Client.connect(
        config.TEMPORAL_HOST,
        namespace=config.TEMPORAL_NAMESPACE,
        tls=tls_config
    )
    
    logger.info("Running legacy Hello World workflow...")
    
    # Execute the workflow
    result = await client.execute_workflow(
        SayHello.run,
        "World",
        id=f"hello-world-{uuid.uuid4()}",
        task_queue=config.TASK_QUEUE,
    )
    
    logger.info(f"Hello World result: {result}")
    return result

async def run_telegram_query_workflow():
    """
    Run the HandleTelegramQuery workflow for demonstration
    This shows how n8n would start the workflow
    """
    
    # Connect to Temporal server
    tls_config = config.TLS_CONFIG if config.TLS_CONFIG else False
    
    client = await Client.connect(
        config.TEMPORAL_HOST,
        namespace=config.TEMPORAL_NAMESPACE,
        tls=tls_config
    )
    
    logger.info("Running HandleTelegramQuery workflow...")
    
    # Create sample request data (what n8n would send)
    request_data = {
        "request_id": str(uuid.uuid4()),
        "chat_id": "123456789",
        "user_id": config.AUTHORIZED_USER_ID,
        "query_text": "What is the weather like today?",
        "timestamp_received": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Starting workflow with request: {request_data['request_id']}")
    
    try:
        # Execute the workflow
        result = await client.execute_workflow(
            HandleTelegramQuery.run,
            request_data,
            id=f"telegram-query-{request_data['request_id']}",
            task_queue=config.TASK_QUEUE,
        )
        
        logger.info(f"Workflow completed successfully!")
        logger.info(f"Request ID: {result.request_id}")
        logger.info(f"Chat ID: {result.chat_id}")
        logger.info(f"Answer: {result.answer_text}")
        logger.info(f"Status: {result.status}")
        
        return result
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        raise

async def get_workflow_result(workflow_id: str):
    """
    Get the result of a running workflow by ID
    This demonstrates how n8n would poll for workflow completion
    """
    
    # Connect to Temporal server
    tls_config = config.TLS_CONFIG if config.TLS_CONFIG else False
    
    client = await Client.connect(
        config.TEMPORAL_HOST,
        namespace=config.TEMPORAL_NAMESPACE,
        tls=tls_config
    )
    
    logger.info(f"Getting workflow result for ID: {workflow_id}")
    
    try:
        # Get workflow handle
        handle = client.get_workflow_handle(workflow_id)
        
        # Get the result (this will wait if workflow is still running)
        result = await handle.result()
        
        logger.info(f"Workflow result retrieved: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to get workflow result: {e}")
        raise

async def main():
    """Main runner function"""
    
    # Check configuration
    if not config.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set - LLM calls will fail")
    
    logger.info("Temporal Workflow Runner")
    logger.info("Choose an option:")
    logger.info("1. Run Hello World (legacy)")
    logger.info("2. Run Telegram Query Workflow")
    logger.info("3. Exit")
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        await run_hello_world()
    elif choice == "2":
        await run_telegram_query_workflow()
    elif choice == "3":
        logger.info("Exiting...")
        return
    else:
        logger.error("Invalid choice")

if __name__ == "__main__":
    asyncio.run(main())
# @@@SNIPEND
