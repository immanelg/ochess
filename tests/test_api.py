import pytest
from async_asgi_testclient import TestClient
from starlette import status


@pytest.mark.skip
@pytest.mark.asyncio
async def test_register(client: TestClient) -> None:
    resp = await client.get("/")

    assert resp.status_code == status.HTTP_200_OK
