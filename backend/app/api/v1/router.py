from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.profiles import router as profiles_router
from app.api.v1.courses import router as courses_router
from app.api.v1.enrollments import router as enrollments_router
from app.api.v1.lessons import router as lessons_router
from app.api.v1.progress import router as progress_router
from app.api.v1.community import router as community_router
router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)
router.include_router(profiles_router)
router.include_router(courses_router)
router.include_router(enrollments_router)
router.include_router(lessons_router)
router.include_router(progress_router)
router.include_router(community_router)
