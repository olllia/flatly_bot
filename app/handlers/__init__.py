from aiogram import Router

from app.handlers.admin import router as admin_router
from app.handlers.errors import router as errors_router
from app.handlers.form import router as form_router
from app.handlers.start import router as start_router

main_router = Router()
main_router.include_router(start_router)
main_router.include_router(form_router)
main_router.include_router(admin_router)
main_router.include_router(errors_router)
