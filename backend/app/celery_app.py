# Re-export celery app from core module for CLI compatibility
# This allows running: celery -A app.celery_app worker
from app.core.celery_app import celery_app, celery, get_celery_app

__all__ = ['celery_app', 'celery', 'get_celery_app']
