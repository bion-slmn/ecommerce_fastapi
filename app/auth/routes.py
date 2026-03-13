from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.auth.dependencies import get_current_user
from app.auth.user_chema import RegisterSchema
from app.database import get_db
from app.models.user import User
from app.auth.jwt import hash_password, verify_password, create_access_token
from datetime import datetime, timedelta

auth_router = APIRouter(prefix="/auth", tags=["auth"])
ACCESS_TOKEN_EXPIRE_HOURS = 24


class LoginSchema(BaseModel):
    email: str
    password: str

@auth_router.post("/register", status_code=201)
def register(body: RegisterSchema, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(
            status_code=409,                        # Conflict
            detail="Email already registered"
        )

    user = User(
        name=body.name,
        email=body.email,
        mobile=body.mobile,
        password_hash=hash_password(body.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return JSONResponse(
        status_code=201,
        content={"id": user.id, "name": user.name, "email": user.email}
    )


@auth_router.post("/login")
def login(body: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(
            status_code=401,                        
            detail="Invalid credentials"
        )
    if not verify_password(body.password, user.password_hash, db, user):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token({"sub": str(user.id), "email": user.email})
    expires_at = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

    return JSONResponse(status_code=200, content={
        "accessToken": token,
        "expiresIn": expires_at.isoformat(),
        "user": {"id": user.id, "name": user.name, "email": user.email}
    })

@auth_router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return JSONResponse(
        status_code=200,
        content={
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "mobile": current_user.mobile,
            "created_at": current_user.created_at.isoformat()
        }
    )