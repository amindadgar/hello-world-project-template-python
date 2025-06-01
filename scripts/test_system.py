#!/usr/bin/env python3
"""
System test script for AI Agent
Tests MongoDB connection, Temporal workflow, and creates sample data
"""

import asyncio
import uuid
import sys
import os
from datetime import datetime

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from database import DatabaseManager
from models import TelegramRequestInput, TelegramRequestUpdate

async def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    print("Testing MongoDB connection...")
    
    try:
        db = DatabaseManager()
        
        # Test creating a request
        test_request = TelegramRequestInput(
            request_id=f"test-{uuid.uuid4()}",
            chat_id="test-chat-123",
            user_id=config.AUTHORIZED_USER_ID,
            query_text="This is a test query for system validation",
            timestamp_received=datetime.utcnow()
        )
        
        doc_id = await db.create_request(test_request, "test-workflow-123")
        print(f"✅ Successfully created test request: {test_request.request_id}")
        
        # Test updating the request
        await db.update_request(
            test_request.request_id,
            TelegramRequestUpdate(
                status="COMPLETED",
                answer_text="This is a test response",
                timestamp_answered=datetime.utcnow()
            )
        )
        print(f"✅ Successfully updated test request")
        
        # Test retrieving the request
        retrieved = await db.get_request_by_id(test_request.request_id)
        if retrieved:
            print(f"✅ Successfully retrieved test request: {retrieved.status}")
        else:
            print("❌ Failed to retrieve test request")
            
        return True
        
    except Exception as e:
        print(f"❌ MongoDB test failed: {e}")
        return False

async def test_temporal_connection():
    """Test Temporal server connection"""
    print("Testing Temporal connection...")
    
    try:
        from temporalio.client import Client
        
        tls_config = config.TLS_CONFIG if config.TLS_CONFIG else False
        
        client = await Client.connect(
            config.TEMPORAL_HOST,
            namespace=config.TEMPORAL_NAMESPACE,
            tls=tls_config
        )
        
        # Test by getting workflow service info
        await client.workflow_service.get_system_info()
        print(f"✅ Successfully connected to Temporal at {config.TEMPORAL_HOST}")
        return True
        
    except Exception as e:
        print(f"❌ Temporal connection test failed: {e}")
        return False

async def create_sample_data():
    """Create sample data for testing the dashboard"""
    print("Creating sample data...")
    
    try:
        db = DatabaseManager()
        
        sample_requests = [
            {
                "query_text": "What is the weather like today?",
                "answer_text": "I don't have access to real-time weather data, but you can check a weather website or app for current conditions.",
                "status": "COMPLETED",
                "sentiment_label": "Neutral"
            },
            {
                "query_text": "Tell me a joke",
                "answer_text": "Why don't scientists trust atoms? Because they make up everything!",
                "status": "COMPLETED", 
                "sentiment_label": "Positive"
            },
            {
                "query_text": "How do I fix my computer?",
                "answer_text": "Try restarting your computer first. If that doesn't work, check for software updates.",
                "status": "COMPLETED",
                "sentiment_label": "Neutral"
            },
            {
                "query_text": "This system is broken!",
                "answer_text": "I apologize for the inconvenience. Let me help you troubleshoot the issue.",
                "status": "COMPLETED",
                "sentiment_label": "Negative"
            },
            {
                "query_text": "Test pending request",
                "answer_text": None,
                "status": "PENDING",
                "sentiment_label": None
            },
            {
                "query_text": "Test failed request",
                "answer_text": None,
                "status": "FAILED",
                "sentiment_label": None
            }
        ]
        
        for i, sample in enumerate(sample_requests):
            request_data = TelegramRequestInput(
                request_id=f"sample-{uuid.uuid4()}",
                chat_id=f"sample-chat-{i}",
                user_id=config.AUTHORIZED_USER_ID,
                query_text=sample["query_text"],
                timestamp_received=datetime.utcnow()
            )
            
            doc_id = await db.create_request(request_data, f"sample-workflow-{i}")
            
            # Update with answer if completed
            if sample["status"] == "COMPLETED":
                await db.update_request(
                    request_data.request_id,
                    TelegramRequestUpdate(
                        status=sample["status"],
                        answer_text=sample["answer_text"],
                        timestamp_answered=datetime.utcnow(),
                        sentiment_label=sample["sentiment_label"],
                        sentiment_score=0.8 if sample["sentiment_label"] == "Positive" else 
                                      -0.3 if sample["sentiment_label"] == "Negative" else 0.0
                    )
                )
            else:
                await db.update_request(
                    request_data.request_id,
                    TelegramRequestUpdate(
                        status=sample["status"],
                        error_message="Sample error message" if sample["status"] == "FAILED" else None
                    )
                )
        
        print(f"✅ Created {len(sample_requests)} sample requests")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False

async def main():
    """Run all system tests"""
    print("🚀 Starting AI Agent System Tests")
    print("=" * 50)
    
    # Check configuration
    print("Checking configuration...")
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "your_openai_api_key_here":
        print("⚠️  Warning: OpenAI API key not configured. LLM calls will fail.")
    else:
        print("✅ OpenAI API key configured")
    
    print(f"✅ MongoDB URI: {config.MONGODB_URI}")
    print(f"✅ Temporal host: {config.TEMPORAL_HOST}")
    print()
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if await test_mongodb_connection():
        tests_passed += 1
    
    if await test_temporal_connection():
        tests_passed += 1
    
    if await create_sample_data():
        tests_passed += 1
    
    print()
    print("=" * 50)
    print(f"System Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! System is ready.")
        print("\nNext steps:")
        print("1. Start the worker: python run_worker.py")
        print("2. View dashboard: python scripts/run_dashboard.py")
        print("3. Test workflow: python run_workflow.py")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 