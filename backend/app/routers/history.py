from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from app.database import get_db
from app.models.user import ChatHistory
from app.schemas import ChatHistoryResponse, ChatResponse

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=ChatHistoryResponse)
async def get_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    subject: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ChatHistory)

    if subject:
        query = query.filter(ChatHistory.subject == subject)

    total = query.count()
    histories = query.order_by(desc(ChatHistory.created_at)).offset(skip).limit(limit).all()

    return ChatHistoryResponse(
        histories=[ChatResponse.model_validate(h) for h in histories],
        total=total
    )


@router.get("/{history_id}", response_model=ChatResponse)
async def get_history_detail(
    history_id: int,
    db: Session = Depends(get_db)
):
    history = db.query(ChatHistory).filter(
        ChatHistory.id == history_id
    ).first()

    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History not found"
        )

    return history
