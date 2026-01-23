from pydantic import BaseModel, Field
from datetime import datetime
from ...utils.timezone import ist_now
from typing import Optional


class RetailerNotificationBase(BaseModel):
    RetailerId: Optional[int]
    Title: Optional[str]
    Message: Optional[str]
    Type: Optional[str]
    IsRead: Optional[bool] = False
    Date: Optional[datetime] = Field(default_factory=ist_now)

    class Config:
        from_attributes = True


class RetailerNotificationCreate(RetailerNotificationBase):
    RetailerId: int
    Title: str
    Message: str
    Type: str


class RetailerNotificationUpdate(BaseModel):
    IsRead: Optional[bool]


class RetailerNotificationRead(RetailerNotificationBase):
    NotificationId: int
