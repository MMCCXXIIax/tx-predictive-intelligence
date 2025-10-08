from typing import Optional, List, Dict, Any
from datetime import datetime

try:
    from pydantic import BaseModel, Field
except Exception:  # fallback to avoid runtime errors if pydantic missing
    class BaseModel:  # type: ignore
        pass
    def Field(*args, **kwargs):  # type: ignore
        return None


class PatternPerformanceQuery(BaseModel):
    window: int = Field(default=30, ge=1, le=365)
    pattern: Optional[str] = None
    symbol: Optional[str] = None


class ProviderStatus(BaseModel):
    ok: bool
    latency_ms: Optional[int] = None
    error: Optional[str] = None


class ProviderHealthResponse(BaseModel):
    success: bool
    data: Dict[str, ProviderStatus]
    timestamp: str


class WorkersHealthResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    timestamp: str
