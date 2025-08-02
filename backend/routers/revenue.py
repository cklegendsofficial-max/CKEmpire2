from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from database import get_db, get_project_by_id, Revenue
from models import RevenueCreate, RevenueModel, RevenueList, SuccessResponse

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.post("/revenue", response_model=RevenueModel, status_code=201)
async def add_revenue(
    revenue: RevenueCreate,
    db: Session = Depends(get_db)
):
    """
    Add revenue to a project
    
    - **project_id**: Project ID (required)
    - **amount**: Revenue amount (required)
    - **source**: Revenue source (required)
    - **description**: Revenue description (optional)
    """
    try:
        # Check if project exists
        project = get_project_by_id(db, revenue.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Create revenue record
        revenue_data = revenue.dict()
        new_revenue = Revenue(**revenue_data)
        db.add(new_revenue)
        
        # Update project revenue
        project.revenue += revenue.amount
        project.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(new_revenue)
        
        logger.info(f"✅ Revenue added: {revenue.amount} for project {revenue.project_id}")
        
        return RevenueModel.from_orm(new_revenue)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to add revenue: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add revenue")

@router.get("/revenue", response_model=RevenueList)
async def get_revenue(
    skip: int = Query(0, ge=0, description="Number of revenue records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of revenue records to return"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    db: Session = Depends(get_db)
):
    """
    Get revenue records with pagination
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Number of records to return (max 1000)
    - **project_id**: Filter by project ID
    """
    try:
        query = db.query(Revenue)
        
        # Filter by project_id if provided
        if project_id:
            query = query.filter(Revenue.project_id == project_id)
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        revenues = query.offset(skip).limit(limit).all()
        
        # Convert to Pydantic models
        revenue_models = [RevenueModel.from_orm(r) for r in revenues]
        
        return RevenueList(
            revenues=revenue_models,
            total=total,
            page=skip // limit + 1,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to get revenue records: {e}")
        raise HTTPException(status_code=500, detail="Failed to get revenue records")

@router.get("/revenue/{revenue_id}", response_model=RevenueModel)
async def get_revenue_by_id(
    revenue_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific revenue record by ID
    
    - **revenue_id**: Revenue record ID
    """
    try:
        revenue = db.query(Revenue).filter(Revenue.id == revenue_id).first()
        
        if not revenue:
            raise HTTPException(status_code=404, detail="Revenue record not found")
        
        return RevenueModel.from_orm(revenue)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get revenue record {revenue_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get revenue record")

@router.get("/revenue/project/{project_id}/summary")
async def get_project_revenue_summary(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get revenue summary for a project
    
    - **project_id**: Project ID
    """
    try:
        # Check if project exists
        project = get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get all revenue records for the project
        revenues = db.query(Revenue).filter(Revenue.project_id == project_id).all()
        
        # Calculate summary
        total_revenue = sum(r.amount for r in revenues)
        revenue_count = len(revenues)
        
        # Group by source
        sources = {}
        for revenue in revenues:
            source = revenue.source
            if source not in sources:
                sources[source] = 0
            sources[source] += revenue.amount
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "total_revenue": total_revenue,
            "revenue_count": revenue_count,
            "sources": sources,
            "average_revenue": total_revenue / revenue_count if revenue_count > 0 else 0,
            "last_updated": project.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get revenue summary for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get revenue summary")

@router.delete("/revenue/{revenue_id}", response_model=SuccessResponse)
async def delete_revenue(
    revenue_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a revenue record
    
    - **revenue_id**: Revenue record ID
    """
    try:
        revenue = db.query(Revenue).filter(Revenue.id == revenue_id).first()
        
        if not revenue:
            raise HTTPException(status_code=404, detail="Revenue record not found")
        
        # Update project revenue
        project = get_project_by_id(db, revenue.project_id)
        if project:
            project.revenue -= revenue.amount
            project.updated_at = datetime.utcnow()
        
        # Delete revenue record
        db.delete(revenue)
        db.commit()
        
        logger.info(f"✅ Revenue record deleted: {revenue_id}")
        
        return SuccessResponse(
            message=f"Revenue record {revenue_id} deleted successfully",
            data={"revenue_id": revenue_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete revenue record {revenue_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete revenue record") 