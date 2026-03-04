from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from app.db.mongodb import get_database
from app.models.notification import NotificationCreate, NotificationResponse, NotificationUpdate
from app.api.deps import get_current_user
from app.models.user import UserResponse

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_read: Optional[bool] = None,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get all notifications for the current user"""
    query = {"user_id": current_user.id}
    
    if is_read is not None:
        query["is_read"] = is_read
    
    notifications = await db.notifications.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    
    for notification in notifications:
        notification["_id"] = str(notification["_id"])
    
    return notifications

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification: NotificationCreate,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """Create a new notification"""
    notification_dict = notification.model_dump()
    notification_dict["user_id"] = current_user.id
    notification_dict["is_read"] = False
    notification_dict["created_at"] = datetime.utcnow()
    notification_dict["read_at"] = None
    
    result = await db.notifications.insert_one(notification_dict)
    notification_dict["_id"] = str(result.inserted_id)
    
    return notification_dict

@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get count of unread notifications"""
    count = await db.notifications.count_documents({
        "user_id": current_user.id,
        "is_read": False
    })
    
    return {"count": count}

@router.put("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: str,
    update: NotificationUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update a notification (mark as read/unread)"""
    try:
        obj_id = ObjectId(notification_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid notification ID")
    
    notification = await db.notifications.find_one({
        "_id": obj_id,
        "user_id": current_user.id
    })
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    update_dict = update.model_dump(exclude_unset=True)
    
    if "is_read" in update_dict and update_dict["is_read"]:
        update_dict["read_at"] = datetime.utcnow()
    elif "is_read" in update_dict and not update_dict["is_read"]:
        update_dict["read_at"] = None
    
    await db.notifications.update_one(
        {"_id": obj_id},
        {"$set": update_dict}
    )
    
    updated_notification = await db.notifications.find_one({"_id": obj_id})
    updated_notification["_id"] = str(updated_notification["_id"])
    
    return updated_notification

@router.post("/mark-all-read", response_model=dict)
async def mark_all_read(
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """Mark all notifications as read"""
    result = await db.notifications.update_many(
        {"user_id": current_user.id, "is_read": False},
        {"$set": {"is_read": True, "read_at": datetime.utcnow()}}
    )
    
    return {"updated": result.modified_count}

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """Delete a notification"""
    try:
        obj_id = ObjectId(notification_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid notification ID")
    
    result = await db.notifications.delete_one({
        "_id": obj_id,
        "user_id": current_user.id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return None

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_notifications(
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """Delete all notifications for the current user"""
    await db.notifications.delete_many({"user_id": current_user.id})
    return None
