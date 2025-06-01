from datetime import datetime
from typing import Optional, Dict, Any, Literal, Annotated
from pydantic import BaseModel, Field, field_validator, ConfigDict
from bson import ObjectId
import uuid

# Custom field for ObjectId - Pydantic v2 compatible
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _info=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class TelegramRequestModel(BaseModel):
    """
    Pydantic model for telegram_requests MongoDB collection
    Matches the schema defined in FR-16 of the requirements
    """
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_instance_id: Optional[str] = None
    chat_id: str
    user_id: int = 265278326  # Default authorized user
    query_text: str
    timestamp_received: datetime
    timestamp_logged: Optional[datetime] = None
    status: Literal["PENDING", "RUNNING", "COMPLETED", "FAILED"] = "PENDING"
    answer_text: Optional[str] = None
    timestamp_answered: Optional[datetime] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    error_message: Optional[str] = None

class TelegramRequestInput(BaseModel):
    """
    Input model for creating new telegram requests
    Used in Temporal workflow input
    """
    request_id: str
    chat_id: str
    user_id: int
    query_text: str
    timestamp_received: datetime

class TelegramRequestUpdate(BaseModel):
    """
    Model for updating telegram request documents
    """
    workflow_instance_id: Optional[str] = None
    status: Optional[Literal["PENDING", "RUNNING", "COMPLETED", "FAILED"]] = None
    answer_text: Optional[str] = None
    timestamp_answered: Optional[datetime] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    error_message: Optional[str] = None

class WorkflowResult(BaseModel):
    """
    Result model returned by Temporal workflow
    Used by n8n to get the final response
    """
    request_id: str
    chat_id: str
    answer_text: str
    status: Literal["COMPLETED", "FAILED"]

class SentimentResult(BaseModel):
    """
    Model for sentiment analysis results
    """
    score: float
    label: str
    confidence: Optional[float] = None 