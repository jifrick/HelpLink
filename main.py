import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.templates import templates, APP_DIR
from app.db.session import SessionLocal
from app.db.init_db import init_db
from app.web import views_public, views_auth, views_user, views_admin
from app.api.router import api_router

STATIC_DIR = os.path.join(APP_DIR, "static")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        db = SessionLocal()
        try:
            init_db(db)
        finally:
            db.close()
    except Exception as e:
        print(f"Lifespan DB initialization warning: {e}")
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Community Public Interest Resource Discovery Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    if exc.status_code == 404:
        return templates.TemplateResponse(
            request=request,
            name="errors/404.html",
            context={"current_user": None},
            status_code=404
        )
    
    # Return HTML response containing exception detail for 400, 401, 403
    return HTMLResponse(
        content=f"<!DOCTYPE html><html><body><h1>{exc.status_code} Error</h1><p>{exc.detail}</p></body></html>",
        status_code=exc.status_code
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    print(f"UNHANDLED ROUTE ERROR: {exc}")
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    return templates.TemplateResponse(
        request=request,
        name="errors/500.html",
        context={"current_user": None, "exc_msg": str(exc)},
        status_code=500
    )

app.include_router(views_public.router)
app.include_router(views_auth.router)
app.include_router(views_user.router)
app.include_router(views_admin.router)

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
