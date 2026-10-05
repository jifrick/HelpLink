from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db

router = APIRouter(prefix="/cron", tags=["cron"])

@router.get("/keepalive")
def keepalive(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint hit by Vercel Cron once a day to prevent Supabase
    from pausing the database due to inactivity.
    """
    try:
        # A simple query to wake up / keep alive the database connection
        db.execute(text("SELECT 1"))
        return {"status": "success", "message": "Supabase kept alive"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
