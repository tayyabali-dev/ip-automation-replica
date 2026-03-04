from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class NotificationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    notification_type: Literal["info", "warning", "success", "error", "transmission"] = "info"
    priority: Literal["low", "medium", "high", "urgent"] = "medium"

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

class NotificationInDB(NotificationBase):
    id: str = Field(alias="_id")
    user_id: str
    is_read: bool = False
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class NotificationResponse(NotificationInDB):
    pass
