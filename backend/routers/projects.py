from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from database import get_db, get_all_projects, get_project_by_id, create_project, update_project, delete_project
from models import ProjectCreate, ProjectUpdate, ProjectModel, ProjectList, SuccessResponse, ErrorResponse
from performance import cache_decorator, performance_monitor

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.post("/projects", response_model=ProjectModel, status_code=201)
async def create_new_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new project
    
    - **name**: Project name (required)
    - **description**: Project description (optional)
    - **status**: Project status (active, inactive, completed, on_hold)
    - **budget**: Project budget
    - **revenue**: Project revenue
    """
    try:
        project_data = project.dict()
        new_project = create_project(db, project_data)
        
        logger.info(f"✅ Project created: {new_project.name}")
        
        return ProjectModel.from_orm(new_project)
        
    except Exception as e:
        logger.error(f"❌ Failed to create project: {e}")
        raise HTTPException(status_code=500, detail="Failed to create project")

@router.get("/projects", response_model=ProjectList)
@cache_decorator(expire=300, key_prefix="projects")  # Cache for 5 minutes
@performance_monitor
async def get_projects(
    skip: int = Query(0, ge=0, description="Number of projects to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of projects to return"),
    status: Optional[str] = Query(None, description="Filter by project status"),
    db: Session = Depends(get_db)
):
    """
    Get all projects with pagination
    
    - **skip**: Number of projects to skip (for pagination)
    - **limit**: Number of projects to return (max 1000)
    - **status**: Filter by project status
    """
    try:
        projects = get_all_projects(db, skip=skip, limit=limit)
        
        # Filter by status if provided
        if status:
            projects = [p for p in projects if p.status == status]
        
        # Convert to Pydantic models
        project_models = [ProjectModel.from_orm(p) for p in projects]
        
        return ProjectList(
            projects=project_models,
            total=len(project_models),
            page=skip // limit + 1,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to get projects: {e}")
        raise HTTPException(status_code=500, detail="Failed to get projects")

@router.get("/projects/{project_id}", response_model=ProjectModel)
@cache_decorator(expire=600, key_prefix="project")  # Cache for 10 minutes
@performance_monitor
async def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific project by ID
    
    - **project_id**: Project ID
    """
    try:
        project = get_project_by_id(db, project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return ProjectModel.from_orm(project)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get project")

@router.put("/projects/{project_id}", response_model=ProjectModel)
async def update_project_endpoint(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a project
    
    - **project_id**: Project ID
    - **project_update**: Project update data
    """
    try:
        # Check if project exists
        existing_project = get_project_by_id(db, project_id)
        if not existing_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Update project
        update_data = {k: v for k, v in project_update.dict().items() if v is not None}
        updated_project = update_project(db, project_id, update_data)
        
        if not updated_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        logger.info(f"✅ Project updated: {updated_project.name}")
        
        return ProjectModel.from_orm(updated_project)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update project")

@router.delete("/projects/{project_id}", response_model=SuccessResponse)
async def delete_project_endpoint(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a project
    
    - **project_id**: Project ID
    """
    try:
        # Check if project exists
        existing_project = get_project_by_id(db, project_id)
        if not existing_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Delete project
        success = delete_project(db, project_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        
        logger.info(f"✅ Project deleted: {project_id}")
        
        return SuccessResponse(
            message=f"Project {project_id} deleted successfully",
            data={"project_id": project_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete project")

@router.get("/projects/{project_id}/stats")
async def get_project_stats(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get project statistics
    
    - **project_id**: Project ID
    """
    try:
        project = get_project_by_id(db, project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Calculate stats
        total_revenue = project.revenue
        budget_utilization = (total_revenue / project.budget * 100) if project.budget > 0 else 0
        profit_margin = ((total_revenue - project.budget) / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "total_revenue": total_revenue,
            "budget": project.budget,
            "budget_utilization": round(budget_utilization, 2),
            "profit_margin": round(profit_margin, 2),
            "status": project.status,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get project stats {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get project stats") 