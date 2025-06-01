import logging
from datetime import timedelta
from typing import Dict, Any
from temporalio import workflow
from temporalio.common import RetryPolicy

import config
from models import WorkflowResult

# Set up logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Import activities, passing them through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from activities import (
        log_initial_request,
        invoke_llm,
        update_request_with_result,
        analyze_sentiment,
        handle_failure,
        say_hello  # Legacy activity for testing
    )

@workflow.defn
class HandleTelegramQuery:
    """
    Main workflow for handling Telegram queries (FR-6)
    Orchestrates the complete AI agent processing pipeline
    """
    
    @workflow.run
    async def run(self, request_data: Dict[str, Any]) -> WorkflowResult:
        """
        Main workflow execution that follows the sequence:
        1. Log Initial Request (FR-7)
        2. Invoke LLM (FR-8) 
        3. Update Log with Result (FR-9)
        4. Optional: Sentiment Analysis (FR-10)
        5. Return Result (FR-11)
        """
        request_id = request_data.get("request_id")
        chat_id = request_data.get("chat_id")
        query_text = request_data.get("query_text")
        
        logger.info(f"Starting HandleTelegramQuery workflow for request: {request_id}")
        
        try:
            # Get workflow instance ID
            workflow_instance_id = workflow.info().workflow_id
            
            # Step 1: Log Initial Request (FR-7)
            await workflow.execute_activity(
                log_initial_request,
                args=[request_data, workflow_instance_id],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=2),
                    maximum_interval=timedelta(seconds=10),
                    maximum_attempts=3,
                )
            )
            
            # Step 2: Invoke LLM with retry policy (FR-8)
            answer_text = await workflow.execute_activity(
                invoke_llm,
                args=[request_id, query_text],
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=config.LLM_RETRY_BACKOFF),
                    maximum_interval=timedelta(seconds=30),
                    maximum_attempts=config.LLM_RETRY_ATTEMPTS,
                    backoff_coefficient=2.0
                )
            )
            
            # Step 3: Update Log with Result (FR-9)
            await workflow.execute_activity(
                update_request_with_result,
                args=[request_id, answer_text, "COMPLETED"],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=2),
                    maximum_interval=timedelta(seconds=10),
                    maximum_attempts=3,
                )
            )
            
            # Step 4: Optional Sentiment Analysis (FR-10)
            if config.SENTIMENT_API_ENABLED:
                try:
                    await workflow.execute_activity(
                        analyze_sentiment,
                        args=[request_id, answer_text],
                        start_to_close_timeout=timedelta(seconds=30),
                        retry_policy=RetryPolicy(
                            initial_interval=timedelta(seconds=2),
                            maximum_interval=timedelta(seconds=10),
                            maximum_attempts=2,  # Less critical, fewer retries
                        )
                    )
                except Exception as e:
                    # Sentiment analysis failure shouldn't fail the whole workflow
                    logger.warning(f"Sentiment analysis failed for {request_id}: {e}")
            
            # Step 5: Return Result (FR-11)
            result = WorkflowResult(
                request_id=request_id,
                chat_id=chat_id,
                answer_text=answer_text,
                status="COMPLETED"
            )
            
            logger.info(f"HandleTelegramQuery workflow completed successfully for request: {request_id}")
            return result
            
        except Exception as e:
            # Handle workflow failure
            error_message = f"Workflow failed: {str(e)}"
            logger.error(f"HandleTelegramQuery workflow failed for request {request_id}: {error_message}")
            
            try:
                # Mark request as failed in database
                await workflow.execute_activity(
                    handle_failure,
                    args=[request_id, error_message],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=2),
                        maximum_interval=timedelta(seconds=10),
                        maximum_attempts=2,
                    )
                )
            except Exception as handle_error:
                logger.error(f"Failed to handle failure for request {request_id}: {handle_error}")
            
            # Return failed result
            return WorkflowResult(
                request_id=request_id,
                chat_id=chat_id,
                answer_text=f"Sorry, I encountered an error processing your request: {error_message}",
                status="FAILED"
            )

# Legacy workflow for backward compatibility and testing
@workflow.defn 
class SayHello:
    """Legacy workflow for testing"""
    
    @workflow.run
    async def run(self, name: str) -> str:
        return await workflow.execute_activity(
            say_hello, name, start_to_close_timeout=timedelta(seconds=5)
        )
