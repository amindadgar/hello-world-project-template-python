// MongoDB initialization script for AI Agent system
// This script runs when MongoDB container starts for the first time

// Switch to the ai_agent_db database
db = db.getSiblingDB('ai_agent_db');

// Create a user for the application
db.createUser({
  user: 'ai_agent_user',
  pwd: 'ai_agent_password',
  roles: [
    {
      role: 'readWrite',
      db: 'ai_agent_db'
    }
  ]
});

// Create the telegram_requests collection
db.createCollection('telegram_requests');

// Create indexes for better performance
db.telegram_requests.createIndex({ "request_id": 1 }, { unique: true });
db.telegram_requests.createIndex({ "workflow_instance_id": 1 });
db.telegram_requests.createIndex({ "status": 1, "timestamp_received": -1 });
db.telegram_requests.createIndex({ 
  "query_text": "text", 
  "answer_text": "text" 
}, {
  name: "text_search_index"
});

// Insert a sample document to test the schema
db.telegram_requests.insertOne({
  "request_id": "sample-request-001",
  "workflow_instance_id": "sample-workflow-001", 
  "chat_id": "123456789",
  "user_id": 265278326,
  "query_text": "Hello, this is a test query",
  "timestamp_received": new Date(),
  "timestamp_logged": new Date(),
  "status": "COMPLETED",
  "answer_text": "This is a sample response from the AI agent",
  "timestamp_answered": new Date(),
  "sentiment_score": 0.8,
  "sentiment_label": "Positive",
  "error_message": null
});

print("AI Agent database initialized successfully!");
print("Created collection: telegram_requests");
print("Created indexes for performance optimization");
print("Added sample document for testing"); 