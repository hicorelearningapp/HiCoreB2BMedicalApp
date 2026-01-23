from pydantic import BaseModel, Field
from datetime import datetime
from ...utils.timezone import ist_now
from typing import Optional


class DistributorNotificationBase(BaseModel):
    DistributorId: Optional[int]
    Title: Optional[str]
    Message: Optional[str]
    Type: Optional[str]
    IsRead: Optional[bool] = False
    Date: Optional[datetime] = Field(default_factory=ist_now)

    class Config:
        from_attributes = True


class DistributorNotificationCreate(DistributorNotificationBase):
    DistributorId: int
    Title: str
    Message: str
    Type: str


class DistributorNotificationUpdate(BaseModel):
    IsRead: Optional[bool]


class DistributorNotificationRead(DistributorNotificationBase):
    NotificationId: int
    CreatedAt: datetime = Field(default_factory=ist_now)
