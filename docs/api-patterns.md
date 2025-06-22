# API Development Guide

FastAPI patterns and endpoint architecture for contributors developing or extending the LLM Calendar Assistant API. This guide covers the essential patterns used throughout the codebase to maintain consistency and reliability.

## API Architecture

### Router Organization
Domain-based routing with clean separation of concerns:

```python
# Domain-specific routers
from app.api.calendar import calendar_router
from app.api.event import event_router
from app.api.health import health_router

# Main router assembly
router = APIRouter()
router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(event_router, prefix="/events", tags=["events"])
router.include_router(calendar_router, prefix="/calendar/auth", tags=["calendar", "auth"])
```

### API Structure
```
app/api/
├── router.py        # Main router assembly and configuration
├── schema.py        # Pydantic models for request/response validation
├── event.py         # Event submission endpoints
├── calendar.py      # Calendar authentication endpoints
└── health.py        # Health check and monitoring endpoints
```

## Endpoint Reference

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/health/` | GET | Basic health check | Status only |
| `/health/ready` | GET | Comprehensive readiness check | All dependencies |
| `/events/` | POST | Submit calendar event request | Task ID + Event ID |
| `/calendar/auth/status` | GET | Check authentication status | Auth state |
| `/calendar/auth/revoke` | POST | Revoke calendar credentials | Confirmation |

**Detailed docs**: [http://localhost:8080/docs](http://localhost:8080/docs) (interactive Swagger UI)

## Implementation Patterns

### Schema-First Design
```python
class EventSchema(BaseModel):
    request_id: UUID = Field(default_factory=uuid4)
    request: str = Field(..., min_length=1)

# FastAPI automatically validates against EventSchema
@event_router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def submit_event(event: EventSchema):
```

### Dependency Injection
```python
# Clean separation of concerns - dependencies injected automatically
@router.post("/")
async def endpoint(
    data: EventSchema,                      # Request validation
    db: Session = Depends(get_db_session)   # Database injection
):
```

### Async Processing Pattern
```python
@router.post("/")
async def endpoint(data: Schema, db: Session = Depends(get_db_session)):
    # 1. Store immediately
    db.add(record)
    db.flush()
    
    # 2. Queue background processing  
    task = process_data.delay(record.id)
    
    # 3. Return immediately
    return {"status": "queued", "task_id": task.id}
```

### Status Codes
```python
# 202 Accepted: Async processing (main pattern)
@router.post("/events/", status_code=status.HTTP_202_ACCEPTED)
async def submit_event(event: EventSchema):
    # Store + queue + return immediately
    return {"status": "queued", "task_id": task.id}

# 200 OK: Synchronous responses
@router.get("/health/")
async def health_check():
    return {"status": "healthy"}
```

### OAuth Authentication
```python
# Token validation dependency
async def get_valid_token() -> str:
    # OAuth token validation logic
    pass

# Protected endpoints
@router.get("/calendar/auth/status")
async def auth_status(token: str = Depends(get_valid_token)):
    return {"authenticated": True}

# Note: OAuth flow happens outside API (Google's authorization server)
```

### Error Handling
```python
try:
    result = await operation()
    return {"status": "success", "data": result}
except SpecificError as e:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Operation failed: {e}"
    ) from e
```

## Benefits

✅ **Scalability**: Async processing with immediate response  
✅ **Type Safety**: Pydantic schema validation throughout  
✅ **Maintainability**: Domain-separated router organization  
✅ **Reliability**: Comprehensive health checks and error handling  
✅ **Monitoring**: Built-in health checks for all dependencies 

---