from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", status_code=201)
async def create_user(db: AsyncSession = Depends(get_db)):
    user = User()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"user_id": user.id}
