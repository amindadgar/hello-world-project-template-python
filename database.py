import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from models import TelegramRequestModel, TelegramRequestUpdate, TelegramRequestInput
import config

# Set up logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages MongoDB connection and operations for telegram requests
    """
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self._connect()
    
    def _connect(self):
        """Establish MongoDB connection"""
        try:
            self.client = MongoClient(config.MONGODB_URI)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[config.MONGODB_DATABASE]
            self.collection = self.db[config.MONGODB_COLLECTION]
            self._create_indexes()
            logger.info(f"Connected to MongoDB: {config.MONGODB_DATABASE}.{config.MONGODB_COLLECTION}")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create necessary indexes for performance"""
        try:
            # Create unique index on request_id
            self.collection.create_index("request_id", unique=True)
            
            # Create index on workflow_instance_id
            self.collection.create_index("workflow_instance_id")
            
            # Create compound index for filtering
            self.collection.create_index([
                ("status", ASCENDING),
                ("timestamp_received", DESCENDING)
            ])
            
            # Create text index for searching query and answer text
            self.collection.create_index([
                ("query_text", "text"),
                ("answer_text", "text")
            ])
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    async def create_request(self, request_data: TelegramRequestInput, workflow_instance_id: str) -> str:
        """
        Create a new telegram request document
        Returns the document's _id
        """
        try:
            document = TelegramRequestModel(
                request_id=request_data.request_id,
                chat_id=request_data.chat_id,
                user_id=request_data.user_id,
                query_text=request_data.query_text,
                timestamp_received=request_data.timestamp_received,
                timestamp_logged=datetime.utcnow(),
                workflow_instance_id=workflow_instance_id,
                status="PENDING"
            )
            
            # Use model_dump instead of dict() for Pydantic v2
            result = self.collection.insert_one(document.model_dump(by_alias=True, exclude={"id"}))
            logger.info(f"Created request document: {request_data.request_id}")
            return str(result.inserted_id)
            
        except DuplicateKeyError:
            logger.error(f"Request with ID {request_data.request_id} already exists")
            raise
        except Exception as e:
            logger.error(f"Failed to create request: {e}")
            raise
    
    async def update_request(self, request_id: str, update_data: TelegramRequestUpdate) -> bool:
        """
        Update an existing telegram request document
        Returns True if update was successful
        """
        try:
            # Filter out None values - use model_dump for Pydantic v2
            update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
            
            if not update_dict:
                return True
            
            result = self.collection.update_one(
                {"request_id": request_id},
                {"$set": update_dict}
            )
            
            if result.matched_count > 0:
                logger.info(f"Updated request: {request_id}")
                return True
            else:
                logger.warning(f"Request not found for update: {request_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update request {request_id}: {e}")
            raise
    
    async def get_request_by_id(self, request_id: str) -> Optional[TelegramRequestModel]:
        """Get a request by request_id"""
        try:
            document = self.collection.find_one({"request_id": request_id})
            if document:
                return TelegramRequestModel(**document)
            return None
        except Exception as e:
            logger.error(f"Failed to get request {request_id}: {e}")
            return None
    
    async def get_request_by_workflow_id(self, workflow_instance_id: str) -> Optional[TelegramRequestModel]:
        """Get a request by workflow_instance_id"""
        try:
            document = self.collection.find_one({"workflow_instance_id": workflow_instance_id})
            if document:
                return TelegramRequestModel(**document)
            return None
        except Exception as e:
            logger.error(f"Failed to get request by workflow ID {workflow_instance_id}: {e}")
            return None
    
    def get_all_requests(self, 
                        limit: int = 100, 
                        skip: int = 0,
                        status_filter: Optional[List[str]] = None,
                        date_from: Optional[datetime] = None,
                        date_to: Optional[datetime] = None,
                        search_text: Optional[str] = None) -> List[TelegramRequestModel]:
        """
        Get requests with filtering and pagination
        Used by Streamlit dashboard
        """
        try:
            # Build query
            query = {}
            
            if status_filter:
                query["status"] = {"$in": status_filter}
            
            if date_from or date_to:
                date_query = {}
                if date_from:
                    date_query["$gte"] = date_from
                if date_to:
                    date_query["$lte"] = date_to
                query["timestamp_received"] = date_query
            
            if search_text:
                query["$text"] = {"$search": search_text}
            
            # Execute query with sorting and pagination
            cursor = self.collection.find(query).sort("timestamp_received", DESCENDING).skip(skip).limit(limit)
            
            documents = list(cursor)
            return [TelegramRequestModel(**doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Failed to get requests: {e}")
            return []
    
    def count_requests(self,
                      status_filter: Optional[List[str]] = None,
                      date_from: Optional[datetime] = None,
                      date_to: Optional[datetime] = None,
                      search_text: Optional[str] = None) -> int:
        """Count requests matching the filters"""
        try:
            # Build query (same as get_all_requests)
            query = {}
            
            if status_filter:
                query["status"] = {"$in": status_filter}
            
            if date_from or date_to:
                date_query = {}
                if date_from:
                    date_query["$gte"] = date_from
                if date_to:
                    date_query["$lte"] = date_to
                query["timestamp_received"] = date_query
            
            if search_text:
                query["$text"] = {"$search": search_text}
            
            return self.collection.count_documents(query)
            
        except Exception as e:
            logger.error(f"Failed to count requests: {e}")
            return 0
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Global database manager instance
db_manager = DatabaseManager() 