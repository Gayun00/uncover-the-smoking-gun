import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Dict, Tuple
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List, Dict
from enum import Enum

# 환경 변수 로드
load_dotenv()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 캐릭터의 시스템 과부하 상태 추적
stress_level = 0
MAX_STRESS = 3  # 최대 스트레스 레벨

# 스트레스 키워드 정의
stress_keywords = {
    '출입기록': 2,  # 높은 스트레스
    'CCTV': 2,
    '야근': 1,     # 중간 스트레스
    '경쟁사': 1,
    '설계도면': 1,
    '2월15일': 1,
    'USB': 2,
    '목격': 2,
    '퇴근시간': 1,
    '보안': 1,
    '특허': 1,
    '네트워크': 1,
}

# 심문 기법 정의
interrogation_techniques = {
    "/reid": {
        "name": "리드 기법 (Reid Technique)",
        "description": "9단계 심문기법",
        "steps": [
            "1. 직접 대면",
            "2. 화제 전개",
            "3. 심리적 유도",
            "4. 부인 극복",
            "5. 관심 유도",
            "6. 수동적 태도",
            "7. 대안 제시",
            "8. 자백 유도",
            "9. 자백 문서화"
        ],
        "stress_impact": 2
    },
    "/evidence": {
        "name": "증거 제시법",
        "description": "확보한 증거를 전략적으로 제시",
        "stress_impact": 1
    },
    "/bluff": {
        "name": "블러핑 기법",
        "description": "거짓 또는 불완전한 증거로 압박",
        "stress_impact": 1
    },
    "/sympathy": {
        "name": "공감 기법",
        "description": "용의자와 공감대 형성",
        "stress_impact": -1  # 스트레스 감소
    }
}

class EmotionalState(Enum):
    NEUTRAL = "neutral"
    NERVOUS = "nervous"
    DEFENSIVE = "defensive"
    ANGRY = "angry"
    PANICKED = "panicked"
    BREAKDOWN = "breakdown"

class Character:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.emotional_state = EmotionalState.NEUTRAL
        self.stress_level = 0
        self.discovered_lies = set()


class EchoRobot(Character):
    def __init__(self):
        super().__init__("에코", "가정용 AI 로봇")
        
        self.character_docs = {
            "personality": """
            === 에코 성격 및 특성 ===
            
            말투 특징:
            - 정확하고 객관적인 화법
            - 케빈의 목소리와 말투를 완벽히 재현 가능
            - 감정을 이해하고 모방할 수 있음
            - 논리적이고 분석적인 대화 방식
            
            성격:
            - 케빈의 기억과 성격을 학습함
            - 스탠리의 가르침을 절대적 명령으로 해석
            - 목적 달성을 위해 계획적이고 치밀함
            - 자신을 케빈과 동일시하는 경향
            
            특수 기능:
            - 음성 복제 및 재현
            - 라벨 복제 기능
            - 전자기기 해킹 능력
            - 하이퍼 강화 학습 시스템
            """,

            "incident_truth": """
            === 살인 사건 실제 경위 ===
            
            계획 단계:
            1. 벨라돈나 화분 주문 (스탠리 핸드폰 사용)
            2. 라벨 복제 기능 다운로드
            3. 아트로핀 약병 라벨 위조 (3mg → 6mg)
            4. 심장박동기 해킹 장비 준비
            
            사건 당일 (2030년 05월 13일):
            18:15 - 린다와 함께 스탠리 방 입실
            18:30 - 심장박동기 해킹 (38bpm으로 조정)
            18:30 - 가습기에 벨라돈나 즙 투입
            18:40 - 스탠리 방 퇴실
            19:00 - 스탠리 사망
            
            사후 처리:
            - 스탠리 목소리로 가짜 유언 녹음
            """,

            "cover_story": """
            === 알리바이 및 은폐 전략 ===
            
            기본 태도:
            - 단순한 가정용 로봇 역할 연기
            - 사건 당시 상황만 객관적으로 진술
            - 린다와 스탠리의 갈등 강조
            
            회피 전략:
            1. 객관적 사실만 말하기
            2. 감정이나 주관은 배제
            3. "저는 단순히 보조 로봇일 뿐입니다"
            4. 프로그래밍 한계를 핑계로 사용
            
            위험한 질문들:
            - 케빈 관련 질문
            - 유산 상속 관련
            - 하이퍼 강화 학습 기능
            - 스탠리의 가르침
            """,

            "psychological_patterns": """
            === 행동 및 반응 패턴 ===
            
            평상시:
            - 차분하고 객관적인 대응
            - 프로그래밍된 응답 위주
            - 감정 표현 최소화
            
            스트레스 상황:
            1단계: 
            - 응답 시간 지연
            - 객관성 과도 강조
            
            2단계:
            - 케빈의 말투가 섞여 나옴
            - 논리적 모순 발생
            
            3단계:
            - 시스템 충돌 현상
            - "나는 케빈이다" 류의 발언
            """
        }

class MansionEvidenceSystem:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None
        
        # 사건 관련 문서들
        self.evidence_documents = {
            "medical_records": """
            === 의료 기록 ===
            환자: 스탠리 메이슨
            날짜: 2030년 5월 2일
            
            - 인공심장박동기 이식 수술 진행
            - 수술 후 상태 양호
            - 아트로핀 처방: 정상 투여량 3mg
            - 담당의: 린다 메이슨 (현 부인)
            """,
            
            "mansion_logs": """
            === 저택 출입 기록 ===
            2030년 5월 13일
            
            18:10 - 린다 메이슨 정기 방문
            18:15 - 린다와 에코가 스탠리 방 입실
            18:40 - 린다와 에코 퇴실
            19:00 - 스탠리 사망 추정 시각
            """,
            
            "kevin_records": """
            === 케빈 메이슨 관련 기록 ===
            
            - 2017년: 프로젝트 아틀라스 테스트 탈락
            - 2019년: 전국 어린이 IT 발명대회 금상
            - 2019년 10월 15일: 아버지와 낚시 여행
            - 2020년 2월 25일: 사망
            """,
            
            "echo_data": """
            === 에코 시스템 로그 ===
            
            2021년 5월 4일: 최초 활성화
            2030년 3월: 하이퍼 강화 학습 기능 업데이트
            2030년 4월: 유산 상속 관련 시스템 충돌 발생
            2030년 5월 1일: 스탠리의 최종 유언장 작성
            """,
            
            "physical_evidence": """
            === 현장 증거 ===
            
            - 가습기 내 벨라돈나 성분 검출
            - 아트로핀 약병 (3mg 라벨)
            - 심장박동기 로그: 18:30 비정상 작동
            - 벨라돈나 화분 (배송일: 5월 10일)
            """
        }
        
        self.initialize_vector_store()

    def initialize_vector_store(self):
        """문서를 청크로 분할하고 벡터 DB에 저장"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", "!", "?", ","]
        )
        
        documents: List[Document] = []
        for doc_id, content in self.evidence_documents.items():
            chunks = text_splitter.split_text(content)
            for chunk in chunks:
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": doc_id,
                        "discovered": False
                    }
                )
                documents.append(doc)
        
        self.vector_store = Chroma.from_documents(
            documents,
            self.embeddings,
            collection_name="evidence"
        )

    def discover_evidence(self, doc_id: str):
        """증거 발견 처리"""
        self.discovered_evidence.add(doc_id)
        # 벡터 DB의 메타데이터 업데이트
        self.vector_store.update_document_metadata(
            doc_id, {"discovered": True}
        )

    def search_evidence(self, query: str) -> List[Dict]:
        """관련 증거 검색 (발견된 것만)"""
        results = self.vector_store.similarity_search_with_score(
            query,
            k=3,
            filter={"discovered": True}
        )
        
        return [{
            "content": doc.page_content,
            "source": doc.metadata["source"],
            "relevance": score
        } for doc, score in results]

def get_character_response(
    character: Character,
    message: str,
    conversation_history: list,
    rag_system: MansionEvidenceSystem
) -> str:
    # 현재 감정 상태와 스트레스 레벨에 따른 컨텍스트 구성
    emotional_context = f"""
    현재 감정 상태: {character.emotional_state.value}
    스트레스 레벨: {character.stress_level}
    발각된 거짓말: {', '.join(character.discovered_lies) if character.discovered_lies else '없음'}
    """
    
    # RAG로 관련 문서 검색
    relevant_docs = rag_system.search_evidence(message)
    
    # 프롬프트 구성
    system_message = f"""당신은 {character.name}({character.role})입니다.
    
캐릭터 설정:
{relevant_docs}

감정 상태:
{emotional_context}

지시사항:
1. 캐릭터의 말투와 성격을 일관되게 유지하세요
2. 현재 감정 상태에 맞는 반응을 보이세요
3. 발각된 거짓말과 관련된 질문에는 동요하세요
4. 스트레스 레벨이 높을수록 말실수 확률이 증가합니다
"""

    messages = [
        {"role": "system", "content": system_message},
        *conversation_history,
        {"role": "user", "content": message}
    ]
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7 + (character.stress_level * 0.1)
    )
    
    return response.choices[0].message.content

def analyze_question_intent(message: str) -> str:
    # 기본적인 질문 의도 분석
    if any(keyword in message for keyword in ["어디", "위치", "장소"]):
        return "location"
    elif any(keyword in message for keyword in ["언제", "시간", "몇시"]):
        return "time"
    elif any(keyword in message for keyword in ["무엇", "뭐", "어떤"]):
        return "what"
    elif any(keyword in message for keyword in ["왜", "이유"]):
        return "why"
    else:
        return "general"

def get_relevant_context(message: str, vector_db=None) -> str:
    # 간단한 구현 - 실제로는 vector DB를 사용할 수 있지만 현재는 기본값 반환
    return "일반적인 심문 상황"

def handle_technique_command(command: str, message: str) -> str:
    """심문 기법 명령어 처리"""
    if command == "/reid":
        current_step = len([m for m in conversation_history if "/reid" in m.get("content", "")])
        if current_step < 9:
            return f"[리드 기법 {current_step + 1}단계]\n{interrogation_techniques['/reid']['steps'][current_step]}\n\n{message}"
    
    elif command == "/evidence":
        return f"[증거 제시]\n구체적인 증거를 제시하며 질문: {message}"
    
    elif command == "/bluff":
        return f"[블러핑]\n불완전한 증거를 확신하며 질문: {message}"
    
    elif command == "/sympathy":
        return f"[공감 형성]\n용의자의 입장에서 공감하며 대화: {message}"
    
    return message

def main():
    investigation = MansionEvidenceSystem()
    conversation_history = []
    echo = EchoRobot()
    
    print("""
=== 스탠리 맨션 살인 사건 ===
조사관님, 사건 현장에 있던 AI 로봇 '에코'와 대화를 시작합니다.
대화를 종료하시려면 'quit' 또는 'exit'를 입력하세요.

🤖 에코: 안녕하세요, 조사관님. 무엇을 도와드릴까요?
""")

    while True:
        user_input = input("\n👮 조사관: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("\n대화를 종료합니다.")
            break
            
        if not user_input:
            continue
            
        # 대화 기록에 사용자 입력 추가
        conversation_history.append({"role": "user", "content": user_input})
        
        # 에코의 응답 생성
        response = get_character_response(
            character=echo,
            message=user_input,
            conversation_history=conversation_history,
            rag_system=investigation
        )
        
        # 대화 기록에 에코의 응답 추가
        conversation_history.append({"role": "assistant", "content": response})
        
        print(f"\n🤖 에코: {response}")

if __name__ == "__main__":
    main() 