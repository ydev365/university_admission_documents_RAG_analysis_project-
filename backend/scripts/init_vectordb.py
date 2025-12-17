"""
ChromaDB 초기화 스크립트
세부능력특기사항 데이터를 파싱하여 ChromaDB에 저장합니다.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from openai import OpenAI
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

import chromadb
from chromadb.config import Settings


# Configuration
DATA_DIR = Path(__file__).parent.parent.parent / "상명대_컴퓨터과학과_합격생들_세부능력및특기사항_data_취합"
CHROMA_PERSIST_DIR = Path(__file__).parent.parent / "chroma_db"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def parse_txt_file(file_path: Path) -> List[Dict[str, str]]:
    """
    txt 파일을 파싱하여 과목별 세특 내용을 추출합니다.
    """
    chunks = []
    file_name = file_path.stem

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    current_subject = None
    current_content = []

    # Pattern to match subject headers
    # Examples: "한국사:", "국어 국어:", "(1학기)수학:", "(2학기)영어:"
    subject_pattern = re.compile(r'^(?:\d+→)?(?:\((?:1|2)학기\)\s*)?([가-힣A-Za-z\s]+?)(?:\s*[IⅠⅡ]+)?(?:\s*\d*)?\s*[:：]')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Remove line number prefix like "1→", "2→"
        if "→" in line:
            parts = line.split("→", 1)
            if len(parts) > 1:
                line = parts[1].strip()

        if not line:
            continue

        # Check if this line starts a new subject
        match = subject_pattern.match(line)
        if match:
            # Save previous subject content
            if current_subject and current_content:
                full_content = " ".join(current_content)
                if len(full_content) > 50:  # Only save meaningful content
                    chunks.append({
                        "subject": normalize_subject(current_subject),
                        "content": full_content,
                        "source_file": file_name
                    })

            # Start new subject
            current_subject = match.group(1).strip()
            # Get content after the colon
            content_after_colon = line[match.end():].strip()
            current_content = [content_after_colon] if content_after_colon else []
        elif current_subject:
            # Continue with current subject
            current_content.append(line)

    # Don't forget the last subject
    if current_subject and current_content:
        full_content = " ".join(current_content)
        if len(full_content) > 50:
            chunks.append({
                "subject": normalize_subject(current_subject),
                "content": full_content,
                "source_file": file_name
            })

    return chunks


def normalize_subject(subject: str) -> str:
    """
    과목명을 정규화합니다.
    """
    subject = subject.strip()

    # Remove duplicates like "국어 국어"
    words = subject.split()
    if len(words) == 2 and words[0] == words[1]:
        subject = words[0]

    # Normalize common variations
    normalizations = {
        "물리학": "물리학I",
        "생명과학": "생명과학I",
        "지구과학": "지구과학I",
        "화학": "화학I",
        "수학": "수학",
        "영어": "영어",
        "기술 . 가정": "기술가정",
        "기술.가정": "기술가정",
        "사회 . 문화": "사회문화",
        "사회.문화": "사회문화",
    }

    return normalizations.get(subject, subject)


def get_embeddings(texts: List[str], client: OpenAI) -> List[List[float]]:
    """
    OpenAI API를 사용하여 텍스트 임베딩을 생성합니다.
    """
    embeddings = []
    batch_size = 100  # OpenAI API batch limit

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=batch
        )
        embeddings.extend([item.embedding for item in response.data])
        print(f"  Embedded {min(i + batch_size, len(texts))}/{len(texts)} documents")

    return embeddings


def init_vectordb():
    """
    메인 초기화 함수
    """
    print("=" * 60)
    print("세부능력특기사항 ChromaDB 초기화 시작")
    print("=" * 60)

    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY가 설정되지 않았습니다.")
        print(".env 파일에 OPENAI_API_KEY를 설정해주세요.")
        return

    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Initialize ChromaDB
    print("\n1. ChromaDB 초기화 중...")
    CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)

    chroma_client = chromadb.PersistentClient(
        path=str(CHROMA_PERSIST_DIR),
        settings=Settings(anonymized_telemetry=False)
    )

    # Delete existing collection if exists
    try:
        chroma_client.delete_collection("setuek_collection")
        print("   기존 컬렉션 삭제됨")
    except:
        pass

    collection = chroma_client.create_collection(
        name="setuek_collection",
        metadata={"description": "세부능력특기사항 데이터"}
    )
    print("   새 컬렉션 생성됨")

    # Parse all txt files
    print("\n2. 데이터 파일 파싱 중...")
    all_chunks = []

    if not DATA_DIR.exists():
        print(f"ERROR: 데이터 디렉토리가 존재하지 않습니다: {DATA_DIR}")
        return

    txt_files = list(DATA_DIR.glob("*.txt"))
    print(f"   발견된 파일 수: {len(txt_files)}")

    for file_path in txt_files:
        chunks = parse_txt_file(file_path)
        all_chunks.extend(chunks)
        print(f"   - {file_path.name}: {len(chunks)} chunks")

    print(f"\n   총 {len(all_chunks)} chunks 추출됨")

    if not all_chunks:
        print("ERROR: 추출된 데이터가 없습니다.")
        return

    # Get subject statistics
    subject_counts = {}
    for chunk in all_chunks:
        subject = chunk["subject"]
        subject_counts[subject] = subject_counts.get(subject, 0) + 1

    print("\n3. 과목별 통계:")
    for subject, count in sorted(subject_counts.items(), key=lambda x: -x[1]):
        print(f"   - {subject}: {count}")

    # Generate embeddings
    print("\n4. 임베딩 생성 중...")
    texts = [f"[{chunk['subject']}] {chunk['content']}" for chunk in all_chunks]
    embeddings = get_embeddings(texts, client)

    # Add to ChromaDB
    print("\n5. ChromaDB에 저장 중...")
    ids = [f"doc_{i}" for i in range(len(all_chunks))]
    documents = [chunk["content"] for chunk in all_chunks]
    metadatas = [{"subject": chunk["subject"], "source_file": chunk["source_file"]} for chunk in all_chunks]

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    print(f"   {len(all_chunks)} documents 저장 완료")

    # Verify
    print("\n6. 저장 확인...")
    count = collection.count()
    print(f"   컬렉션 내 문서 수: {count}")

    print("\n" + "=" * 60)
    print("ChromaDB 초기화 완료!")
    print("=" * 60)


if __name__ == "__main__":
    init_vectordb()
