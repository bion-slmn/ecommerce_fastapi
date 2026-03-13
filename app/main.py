# app/main.py
from fastapi import FastAPI, Request
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.auth.middleware import JWTMiddleware
from app.auth.routes import auth_router
from app.routers.products import router as product_router
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Middleware
app.add_middleware(JWTMiddleware)

# Routers
app.include_router(auth_router)
app.include_router(product_router)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z"  # UTC ISO format
    }

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {
            "field": err["loc"][-1],   # e.g "email", "password"
            "message": err["msg"].replace("Value error, ", "")
        }
        for err in exc.errors()
    ]
    return JSONResponse(status_code=400, content={"detail": errors})