# @@@SNIPSTART python-project-template-activities
import logging
import asyncio
from datetime import datetime
from typing import Optional
from temporalio import activity
import openai
import config
from database import db_manager
from models import TelegramRequestInput, TelegramRequestUpdate, SentimentResult

# Set up logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Configure OpenAI
openai.api_key = config.OPENAI_API_KEY

@activity.defn
async def log_initial_request(request_data: dict, workflow_instance_id: str) -> str:
    """
    Activity: Log Initial Request (FR-7)
    Persist initial record to MongoDB with PENDING status
    """
    try:
        # Convert dict to TelegramRequestInput
        request_input = TelegramRequestInput(**request_data)
        
        # Log the request to MongoDB
        document_id = await db_manager.create_request(request_input, workflow_instance_id)
        
        # Update status to RUNNING
        await db_manager.update_request(
            request_input.request_id,
            TelegramRequestUpdate(status="RUNNING")
        )
        
        logger.info(f"Logged initial request: {request_input.request_id}")
        return document_id
        
    except Exception as e:
        logger.error(f"Failed to log initial request: {e}")
        # Update status to FAILED
        await db_manager.update_request(
            request_data.get("request_id", "unknown"),
            TelegramRequestUpdate(
                status="FAILED",
                error_message=f"Failed to log request: {str(e)}"
            )
        )
        raise

@activity.defn
async def invoke_llm(request_id: str, query_text: str) -> str:
    """
    Activity: Invoke LLM (FR-8)
    Call OpenAI's chat endpoint with retry logic
    """
    try:
        logger.info(f"Invoking LLM for request: {request_id}")
        
        # Prepare the prompt
        messages = [
            {
                "role": "system",
                "content": "Answer the query with a very concise response."
            },
            {
                "role": "user",
                "content": f"Query: {query_text}"
            }
        ]
        
        # Call OpenAI API
        response = await asyncio.to_thread(
            openai.chat.completions.create,
            model=config.OPENAI_MODEL,
            messages=messages,
            max_tokens=200,
            temperature=0.7
        )
        
        answer_text = response.choices[0].message.content.strip()
        logger.info(f"LLM response received for request: {request_id}")
        
        return answer_text
        
    except Exception as e:
        logger.error(f"LLM invocation failed for request {request_id}: {e}")
        # Log error to database
        await db_manager.update_request(
            request_id,
            TelegramRequestUpdate(
                status="FAILED",
                error_message=f"LLM invocation failed: {str(e)}"
            )
        )
        raise

@activity.defn
async def update_request_with_result(request_id: str, answer_text: str, status: str) -> bool:
    """
    Activity: Update Log with LLM Result (FR-9)
    Update MongoDB document with final answer and status
    """
    try:
        logger.info(f"Updating request with result: {request_id}")
        
        update_data = TelegramRequestUpdate(
            status=status,
            answer_text=answer_text,
            timestamp_answered=datetime.utcnow()
        )
        
        success = await db_manager.update_request(request_id, update_data)
        
        if success:
            logger.info(f"Successfully updated request: {request_id}")
        else:
            logger.warning(f"Failed to update request: {request_id}")
        
        return success
        
    except Exception as e:
        logger.error(f"Failed to update request result {request_id}: {e}")
        raise

@activity.defn
async def analyze_sentiment(request_id: str, text: str) -> Optional[SentimentResult]:
    """
    Activity: Enrichment - Sentiment Analysis (FR-10)
    Optional sentiment analysis on the answer text
    """
    try:
        if not config.SENTIMENT_API_ENABLED:
            logger.info("Sentiment analysis is disabled")
            return None
        
        logger.info(f"Analyzing sentiment for request: {request_id}")
        
        # Simple sentiment analysis using OpenAI
        # In production, you might use a dedicated sentiment API
        messages = [
            {
                "role": "system", 
                "content": "Analyze the sentiment of the following text. Respond with only a JSON object containing 'score' (float between -1 and 1, where -1 is most negative, 1 is most positive) and 'label' (Positive, Negative, or Neutral)."
            },
            {
                "role": "user",
                "content": f"Text: {text}"
            }
        ]
        
        response = await asyncio.to_thread(
            openai.chat.completions.create,
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=50,
            temperature=0.1
        )
        
        # Parse the response (simplified - in production, add error handling)
        import json
        try:
            sentiment_data = json.loads(response.choices[0].message.content.strip())
            sentiment_result = SentimentResult(
                score=float(sentiment_data.get("score", 0)),
                label=sentiment_data.get("label", "Neutral")
            )
        except:
            # Fallback to neutral sentiment
            sentiment_result = SentimentResult(score=0.0, label="Neutral")
        
        # Update the database with sentiment data
        await db_manager.update_request(
            request_id,
            TelegramRequestUpdate(
                sentiment_score=sentiment_result.score,
                sentiment_label=sentiment_result.label
            )
        )
        
        logger.info(f"Sentiment analysis completed for request: {request_id}")
        return sentiment_result
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed for request {request_id}: {e}")
        # Don't fail the whole workflow for sentiment analysis
        return None

@activity.defn
async def handle_failure(request_id: str, error_message: str) -> bool:
    """
    Activity: Handle workflow failures
    Mark request as FAILED with error message
    """
    try:
        logger.info(f"Handling failure for request: {request_id}")
        
        update_data = TelegramRequestUpdate(
            status="FAILED",
            error_message=error_message,
            timestamp_answered=datetime.utcnow()
        )
        
        success = await db_manager.update_request(request_id, update_data)
        logger.info(f"Marked request as failed: {request_id}")
        
        return success
        
    except Exception as e:
        logger.error(f"Failed to handle failure for request {request_id}: {e}")
        return False

# Legacy activity for backward compatibility
@activity.defn
async def say_hello(name: str) -> str:
    """Legacy hello activity for testing"""
    return f"Hello, {name}!"

# @@@SNIPEND
