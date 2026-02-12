from fastapi import APIRouter
from app.api.endpoints import auth, documents, jobs, applications, enhanced_applications

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(enhanced_applications.router, tags=["enhanced-applications"])
from app.api.endpoints import office_actions
api_router.include_router(office_actions.router, prefix="/office-actions", tags=["office-actions"])