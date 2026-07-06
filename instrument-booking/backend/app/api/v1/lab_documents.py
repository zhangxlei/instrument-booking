import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.lab_document import LabDocument
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.lab_document import LabDocumentCreate, LabDocumentRead

router = APIRouter(prefix="/lab-documents", tags=["通知文档"])


@router.get("", response_model=list[LabDocumentRead])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(LabDocument).where(LabDocument.is_published == True).order_by(LabDocument.created_at.desc())
    )
    return result.scalars().all()


@router.get("/login-notice", response_model=LabDocumentRead | None)
async def get_login_notice(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LabDocument).where(
            LabDocument.is_login_notice == True,
            LabDocument.is_published == True,
        ).order_by(LabDocument.created_at.desc()).limit(1)
    )
    return result.scalar_one_or_none()


@router.post("", response_model=LabDocumentRead, status_code=201)
async def create_document(
    data: LabDocumentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    doc = LabDocument(**data.model_dump())
    db.add(doc)
    await db.flush()
    return doc


@router.put("/{doc_id}", response_model=LabDocumentRead)
async def update_document(
    doc_id: uuid.UUID,
    data: LabDocumentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    doc = await db.get(LabDocument, doc_id)
    if doc is None:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
    for key, val in data.model_dump().items():
        setattr(doc, key, val)
    return doc


@router.delete("/{doc_id}", response_model=MessageResponse)
async def delete_document(
    doc_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    doc = await db.get(LabDocument, doc_id)
    if doc is None:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
    await db.delete(doc)
    return MessageResponse(message="文档已删除")
