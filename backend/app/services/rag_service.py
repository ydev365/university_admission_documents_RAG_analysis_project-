from openai import OpenAI
from typing import List, Optional
from app.config import get_settings
from app.services.vectordb import VectorDBService

settings = get_settings()


class RAGService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.vectordb = VectorDBService()
        self.embedding_model = "text-embedding-3-small"
        self.chat_model = "gpt-4o-mini"

    def get_embedding(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding

    def search_similar_documents(
        self,
        query: str,
        subject: Optional[str] = None,
        n_results: int = 5
    ) -> List[dict]:
        query_embedding = self.get_embedding(query)

        where_filter = None
        if subject:
            where_filter = {"subject": subject}

        results = self.vectordb.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter
        )

        documents = []
        if results and results.get("documents") and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                distance = results["distances"][0][i] if results.get("distances") else 0
                documents.append({
                    "content": doc,
                    "metadata": metadata,
                    "distance": distance
                })

        return documents

    async def get_answer(self, subject: str, question: str) -> str:
        # Search for similar documents
        similar_docs = self.search_similar_documents(
            query=f"{subject} {question}",
            subject=subject,
            n_results=5
        )

        # Build context from retrieved documents
        context = ""
        if similar_docs:
            context_parts = []
            for i, doc in enumerate(similar_docs, 1):
                context_parts.append(f"[참고자료 {i}]\n{doc['content']}")
            context = "\n\n".join(context_parts)

        # Build prompt
        system_prompt = """당신은 고등학생들의 세부능력특기사항(세특) 작성을 도와주는 전문 컨설턴트입니다.
주어진 참고자료는 실제 대학 합격생들의 세부능력특기사항 내용입니다.
이 자료들을 참고하여 학생들이 세특에 어떤 내용을 작성하면 좋을지 조언해주세요.

답변 시 다음 사항을 지켜주세요:
1. 참고자료의 좋은 예시들을 바탕으로 구체적인 조언을 제공하세요.
2. 단순히 참고자료를 복사하지 말고, 학생이 참고할 수 있는 방향성과 아이디어를 제시하세요.
3. 해당 과목에서 어떤 활동, 탐구, 발표 등을 하면 좋을지 구체적으로 제안하세요.
4. 학생의 진로와 연결할 수 있는 방법도 함께 제안하세요.
5. 친절하고 격려하는 톤으로 답변하세요."""

        user_prompt = f"""[과목] {subject}

[학생 질문]
{question}

[참고자료 - 합격생들의 세특 내용]
{context if context else "관련 참고자료가 없습니다."}

위 참고자료를 바탕으로 학생의 질문에 답변해주세요."""

        # Call OpenAI API
        response = self.client.chat.completions.create(
            model=self.chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        return response.choices[0].message.content
