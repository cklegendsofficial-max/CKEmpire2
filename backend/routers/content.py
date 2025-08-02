from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db, get_content_by_id, get_content_by_project, create_content, update_content, delete_content, Content
from models import ContentCreate, ContentUpdate, ContentResponse, SuccessResponse

router = APIRouter()

@router.post("/content", response_model=ContentResponse, status_code=201)
async def create_content_item(
    content: ContentCreate,
    db: Session = Depends(get_db)
):
    """Create new content item"""
    try:
        content_data = content.dict()
        content_data["created_at"] = datetime.utcnow()
        content_data["updated_at"] = datetime.utcnow()
        
        db_content = create_content(db, content_data)
        
        return ContentResponse(
            id=db_content.id,
            project_id=db_content.project_id,
            title=db_content.title,
            content_type=db_content.content_type,
            content_data=db_content.content_data,
            metadata=db_content.metadata,
            status=db_content.status,
            ai_generated=db_content.ai_generated,
            created_at=db_content.created_at,
            updated_at=db_content.updated_at,
            published_at=db_content.published_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create content: {str(e)}")

@router.get("/content", response_model=List[ContentResponse])
async def get_content_items(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """Get content items with optional filtering"""
    try:
        query = db.query(Content)
        
        if project_id:
            query = query.filter(Content.project_id == project_id)
        if content_type:
            query = query.filter(Content.content_type == content_type)
        if status:
            query = query.filter(Content.status == status)
            
        content_items = query.offset(skip).limit(limit).all()
        
        return [
            ContentResponse(
                id=item.id,
                project_id=item.project_id,
                title=item.title,
                content_type=item.content_type,
                content_data=item.content_data,
                metadata=item.metadata,
                status=item.status,
                ai_generated=item.ai_generated,
                created_at=item.created_at,
                updated_at=item.updated_at,
                published_at=item.published_at
            )
            for item in content_items
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve content: {str(e)}")

@router.get("/content/{content_id}", response_model=ContentResponse)
async def get_content_item(
    content_id: int,
    db: Session = Depends(get_db)
):
    """Get specific content item by ID"""
    try:
        content = get_content_by_id(db, content_id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return ContentResponse(
            id=content.id,
            project_id=content.project_id,
            title=content.title,
            content_type=content.content_type,
            content_data=content.content_data,
            metadata=content.metadata,
            status=content.status,
            ai_generated=content.ai_generated,
            created_at=content.created_at,
            updated_at=content.updated_at,
            published_at=content.published_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve content: {str(e)}")

@router.put("/content/{content_id}", response_model=ContentResponse)
async def update_content_item(
    content_id: int,
    content_update: ContentUpdate,
    db: Session = Depends(get_db)
):
    """Update content item"""
    try:
        content = get_content_by_id(db, content_id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        update_data = content_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        updated_content = update_content(db, content_id, update_data)
        
        return ContentResponse(
            id=updated_content.id,
            project_id=updated_content.project_id,
            title=updated_content.title,
            content_type=updated_content.content_type,
            content_data=updated_content.content_data,
            metadata=updated_content.metadata,
            status=updated_content.status,
            ai_generated=updated_content.ai_generated,
            created_at=updated_content.created_at,
            updated_at=updated_content.updated_at,
            published_at=updated_content.published_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update content: {str(e)}")

@router.delete("/content/{content_id}", response_model=SuccessResponse)
async def delete_content_item(
    content_id: int,
    db: Session = Depends(get_db)
):
    """Delete content item"""
    try:
        content = get_content_by_id(db, content_id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        success = delete_content(db, content_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete content")
        
        return SuccessResponse(message="Content deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete content: {str(e)}")

@router.get("/content/project/{project_id}", response_model=List[ContentResponse])
async def get_content_by_project_id(
    project_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """Get all content for a specific project"""
    try:
        content_items = get_content_by_project(db, project_id, skip, limit)
        
        return [
            ContentResponse(
                id=item.id,
                project_id=item.project_id,
                title=item.title,
                content_type=item.content_type,
                content_data=item.content_data,
                metadata=item.metadata,
                status=item.status,
                ai_generated=item.ai_generated,
                created_at=item.created_at,
                updated_at=item.updated_at,
                published_at=item.published_at
            )
            for item in content_items
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve project content: {str(e)}")

@router.post("/content/{content_id}/publish", response_model=ContentResponse)
async def publish_content(
    content_id: int,
    db: Session = Depends(get_db)
):
    """Publish content item"""
    try:
        content = get_content_by_id(db, content_id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        update_data = {
            "status": "published",
            "published_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        updated_content = update_content(db, content_id, update_data)
        
        return ContentResponse(
            id=updated_content.id,
            project_id=updated_content.project_id,
            title=updated_content.title,
            content_type=updated_content.content_type,
            content_data=updated_content.content_data,
            metadata=updated_content.metadata,
            status=updated_content.status,
            ai_generated=updated_content.ai_generated,
            created_at=updated_content.created_at,
            updated_at=updated_content.updated_at,
            published_at=updated_content.published_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish content: {str(e)}") 