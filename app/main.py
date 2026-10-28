from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.models import Service


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="CloudOps Platform API",
    description="Portfolio REST API for DevOps and cloud operations practice.",
    version="0.2.0",
    lifespan=lifespan,
)


class ServiceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    environment: str = Field(default="dev", pattern="^(dev|staging|production)$")
    status: str = Field(default="healthy", pattern="^(healthy|degraded|down)$")


class ServiceRecord(ServiceCreate):
    id: UUID
    created_at: datetime


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "app": "CloudOps Platform API",
        "version": app.version,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {"status": "healthy", "app": "cloudops-platform-api"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {"status": "ready", "database": "connected"}


@app.get("/api/v1/services", response_model=list[ServiceRecord])
def list_services(db: Session = Depends(get_db)):
    return db.scalars(select(Service).order_by(Service.created_at.desc())).all()


@app.post("/api/v1/services", response_model=ServiceRecord, status_code=201)
def create_service(payload: ServiceCreate, db: Session = Depends(get_db)):
    record = Service(
        id=str(uuid4()),
        name=payload.name,
        environment=payload.environment,
        status=payload.status,
        created_at=datetime.now(timezone.utc),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/api/v1/services/{service_id}", response_model=ServiceRecord)
def get_service(service_id: UUID, db: Session = Depends(get_db)):
    record = db.get(Service, str(service_id))
    if record is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return record


@app.delete("/api/v1/services/{service_id}", status_code=204)
def delete_service(service_id: UUID, db: Session = Depends(get_db)):
    record = db.get(Service, str(service_id))
    if record is None:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(record)
    db.commit()
    return None
