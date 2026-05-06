import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.advanced import SystemConfig
from app.schemas.advanced import SystemConfigCreate, SystemConfigResponse

router = APIRouter(prefix="/api/system", tags=["系统"])


@router.get("/config", response_model=list[SystemConfigResponse])
async def list_configs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(SystemConfig).order_by(SystemConfig.key))
    return result.scalars().all()


@router.put("/config/{key}", response_model=SystemConfigResponse)
async def update_config(
    key: str,
    data: SystemConfigCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(SystemConfig).where(SystemConfig.key == key))
    config = result.scalar_one_or_none()

    if config:
        config.value = data.value
        if data.description is not None:
            config.description = data.description
        await db.flush()
    else:
        config = SystemConfig(
            key=key,
            value=data.value,
            description=data.description,
        )
        db.add(config)
        await db.flush()

    return config


@router.delete("/config/{key}", status_code=204)
async def delete_config(
    key: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(SystemConfig).where(SystemConfig.key == key))
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="配置项不存在")
    await db.delete(config)
