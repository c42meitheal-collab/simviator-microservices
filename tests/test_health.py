"""
Basic health check tests for microservices.
"""
import pytest
import httpx
from .conftest import TestConfig


@pytest.mark.asyncio
async def test_simviator_health(http_client: httpx.AsyncClient):
    """Test simviator service health endpoint."""
    url = f"{TestConfig.get_service_url('simviator')}/health"
    response = await http_client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert data["service"] == "simviator"


@pytest.mark.asyncio
async def test_bot_control_health(http_client: httpx.AsyncClient):
    """Test bot control service health endpoint."""
    url = f"{TestConfig.get_service_url('bot_control')}/health"
    response = await http_client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert data["service"] == "bot_control"


@pytest.mark.asyncio
async def test_orchestrator_health(http_client: httpx.AsyncClient):
    """Test orchestrator service health endpoint."""
    url = f"{TestConfig.get_service_url('orchestrator')}/health"
    response = await http_client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert data["service"] == "orchestrator"


@pytest.mark.asyncio
async def test_orchestrator_status(http_client: httpx.AsyncClient):
    """Test orchestrator service status endpoint."""
    url = f"{TestConfig.get_service_url('orchestrator')}/status"
    response = await http_client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    assert isinstance(data["services"], list)
