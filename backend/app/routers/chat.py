from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import ChatHistory
from app.schemas import ChatRequest, ChatResponse, SubjectListResponse
from app.services.rag_service import RAGService

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Subject list extracted from data
SUBJECTS = [
    "국어", "수학", "영어", "한국사",
    "통합사회", "통합과학", "과학탐구실험",
    "물리학I", "물리학II", "생명과학I", "생명과학II",
    "지구과학I", "지구과학II", "화학I", "화학II",
    "문학", "독서", "화법과작문", "언어와매체",
    "수학I", "수학II", "미적분", "확률과통계", "기하",
    "영어I", "영어II", "영어독해와작문", "영미문학읽기", "실용영어", "진로영어",
    "사회문화", "윤리와사상", "생활과윤리", "한국지리", "세계지리", "경제", "정치와법",
    "일본어I", "일본어II", "중국어I", "중국어II",
    "체육", "운동과건강", "스포츠생활",
    "미술", "미술감상과비평", "음악", "음악감상과비평",
    "정보", "기술가정", "심리학", "교육학", "사회문제탐구",
    "수학과제탐구", "고전과윤리", "생활과한문", "민주시민"
]


@router.get("/subjects", response_model=SubjectListResponse)
async def get_subjects():
    return SubjectListResponse(subjects=sorted(SUBJECTS))


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    try:
        # Initialize RAG service
        rag_service = RAGService()

        # Get answer from RAG
        answer = await rag_service.get_answer(
            subject=request.subject,
            question=request.question
        )

        # Save to chat history
        chat_history = ChatHistory(
            subject=request.subject,
            question=request.question,
            answer=answer
        )

        db.add(chat_history)
        db.commit()
        db.refresh(chat_history)

        return chat_history

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat: {str(e)}"
        )
