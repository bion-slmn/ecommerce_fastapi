# app/auth/dependencies.py
from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User    

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = db.query(User).filter(User.id == int(user_id)).first()  # ✅ User (class) vs user (result)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user