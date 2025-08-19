"""
Test configuration and utilities for simviator microservices.
"""
import pytest
import httpx
from typing import AsyncGenerator


@pytest.fixture
async def http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create HTTP client for testing."""
    async with httpx.AsyncClient() as client:
        yield client


@pytest.fixture
def service_base_url() -> str:
    """Base URL for service testing."""
    return "http://localhost"


class TestConfig:
    """Test configuration constants."""
    SIMVIATOR_PORT = 8001
    BOT_CONTROL_PORT = 8002
    ORCHESTRATOR_PORT = 8000
    
    @classmethod
    def get_service_url(cls, service: str) -> str:
        """Get URL for a specific service."""
        ports = {
            "simviator": cls.SIMVIATOR_PORT,
            "bot_control": cls.BOT_CONTROL_PORT,
            "orchestrator": cls.ORCHESTRATOR_PORT,
        }
        return f"http://localhost:{ports[service]}"
