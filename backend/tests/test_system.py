import uuid
import pytest

from app.models.advanced import SystemConfig


@pytest.mark.asyncio
async def test_list_configs_requires_auth(client):
    response = await client.get("/api/system/config")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_configs(client, auth_headers, db):
    config = SystemConfig(key="test_key", value="test_value", description="测试配置")
    db.add(config)
    await db.commit()

    response = await client.get("/api/system/config", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_update_config_create(client, auth_headers, db):
    response = await client.put(
        "/api/system/config/new_key",
        json={"key": "new_key", "value": "new_value"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "new_key"
    assert data["value"] == "new_value"


@pytest.mark.asyncio
async def test_update_config_create_with_description(client, auth_headers, db):
    response = await client.put(
        "/api/system/config/desc_key",
        json={"key": "desc_key", "value": "value", "description": "描述信息"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "描述信息"


@pytest.mark.asyncio
async def test_update_config_update(client, auth_headers, db):
    config = SystemConfig(key="update_key", value="old_value", description="旧描述")
    db.add(config)
    await db.commit()

    response = await client.put(
        "/api/system/config/update_key",
        json={"key": "update_key", "value": "updated_value"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == "updated_value"


@pytest.mark.asyncio
async def test_delete_config(client, auth_headers, db):
    config = SystemConfig(key="delete_key", value="delete_value")
    db.add(config)
    await db.commit()

    response = await client.delete("/api/system/config/delete_key", headers=auth_headers)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_config_not_found(client, auth_headers):
    response = await client.delete(
        "/api/system/config/nonexistent_key_12345",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_config_requires_auth(client):
    response = await client.delete("/api/system/config/some_key")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_config_requires_auth(client):
    response = await client.put(
        "/api/system/config/key",
        json={"key": "key", "value": "value"},
    )
    assert response.status_code == 401
