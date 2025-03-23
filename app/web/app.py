import streamlit as st
from PIL import Image
import os
import sys
sys.path.append("app")  # app 디렉토리를 Python 경로에 추가
from openai import OpenAI
from dotenv import load_dotenv
from core.rag import EvidenceRAG
from data.echo_data import ECHO_PERSONALITY

from data.scenes import MANSION_SCENES, EVIDENCE_DETAILS

# OpenAI 클라이언트 초기화
load_dotenv()
client = OpenAI()

# 전역 RAG 시스템 초기화
rag_system = EvidenceRAG()

# 세션 상태 초기화
def init_session_state():
    if "current_scene" not in st.session_state:
        st.session_state.current_scene = "mansion_entrance"
    if "evidence" not in st.session_state:
        st.session_state.evidence = set()
    if "messages" not in st.session_state:
        st.session_state.messages = []

def show_scene(scene_id):
    scene = MANSION_SCENES[scene_id]
    st.header(f"🏰 {scene['name']}")
    st.write(scene["description"])
    
    # 조사 가능한 지점들
    st.subheader("조사할 수 있는 곳")
    for spot_id, spot_desc in scene["evidence_spots"].items():
        if st.button(f"🔍 {spot_id} 조사하기", key=f"investigate_{scene_id}_{spot_id}"):
            evidence = handle_investigation(scene_id, spot_id)
            if evidence:
                st.success(f"발견: {evidence}")
    
    # 이동 가능한 장소들
    st.subheader("이동 가능한 장소")
    for next_scene in scene["next_scenes"]:
        if st.button(f"🚪 {MANSION_SCENES[next_scene]['name']}으로 이동", 
                    key=f"move_to_{next_scene}"):
            st.session_state.current_scene = next_scene
            st.rerun()

def handle_investigation(scene_id: str, spot_id: str) -> str:
    """특정 지점 조사 처리"""
    evidence_mapping = {
        # 정원
        ("garden", "flower_bed"): "벨라돈나_화분",
        
        # 스탠리의 방
        ("stanley_room", "humidifier"): "벨라돈나_화분",
        ("stanley_room", "medical_records"): "의료기록",
        ("stanley_room", "pacemaker"): "심장박동기_로그",
        
        # 주방
        ("kitchen", "medicine_cabinet"): "의료기록",
        ("kitchen", "sink"): "약병_증거",
        
        # 화장실
        ("bathroom", "cabinet"): "의료기록",
        ("bathroom", "trash"): "약병_증거",
        
        # 거실
        ("living_room", "coffee_table"): "약병_증거",
        ("living_room", "security_panel"): "보안_로그"
    }
    
    if (scene_id, spot_id) in evidence_mapping:
        evidence = evidence_mapping[(scene_id, spot_id)]
        if evidence in EVIDENCE_DETAILS:  # 증거가 정의되어 있는지 확인
            st.session_state.evidence.add(evidence)
            return EVIDENCE_DETAILS[evidence]["description"]
    
    return "특별한 것을 발견하지 못했습니다."

def get_echo_response(user_input: str) -> str:
    # 관련 증거 검색
    relevant_evidence = rag_system.search_evidence(user_input)
    evidence_context = "\n".join([
        f"- {ev['source']}: {ev['content']}"
        for ev in relevant_evidence
    ])
    
    # 스트레스 레벨 계산 (발견된 증거 수에 따라)
    stress_level = "low" if len(st.session_state.evidence) < 3 else \
                  "medium" if len(st.session_state.evidence) < 5 else "high"
    
    # 컨텍스트 구성
    context = f"""
{ECHO_PERSONALITY['base_setting']}

현재 상태:
- 스트레스 레벨: {stress_level}
- 발견된 증거: {len(st.session_state.evidence)}개

관련 증거:
{evidence_context}

지시사항:
1. {stress_level} 스트레스 수준에 맞는 반응을 보이세요
2. 발견된 증거와 관련된 질문에는 동요하세요
3. 진실은 최대한 숨기되, 스트레스 상황에서는 실수할 수 있습니다
4. 케빈의 목소리/성격은 스트레스가 높을 때 더 자주 나타납니다
"""
    
    messages = [
        {"role": "system", "content": context},
        {"role": "user", "content": user_input}
    ]
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7 + (len(st.session_state.evidence) * 0.1)
    )
    
    return response.choices[0].message.content

def main():
    st.set_page_config(
        page_title="스탠리 맨션 살인 사건",
        page_icon="🔍",
        layout="wide"
    )
    
    init_session_state()
    
    # 2단 레이아웃
    col1, col2 = st.columns([2, 1])
    
    with col1:
        show_scene(st.session_state.current_scene)
        
    with col2:
        st.title("💬 에코와의 대화")
        
        # 대화 이력 표시
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # 사용자 입력
        user_input = st.chat_input("조사관의 질문:")
        if user_input:
            # 사용자 메시지 추가
            st.chat_message("user").write(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # 에코의 응답 생성
            response = get_echo_response(user_input)
            
            # 에코의 응답 표시 및 저장
            st.chat_message("assistant").write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    # 사이드바에 증거 목록 표시
    st.sidebar.title("📑 수집한 증거")
    for evidence in st.session_state.evidence:
        st.sidebar.info(f"🔍 {evidence}: {EVIDENCE_DETAILS[evidence]['description']}")

if __name__ == "__main__":
    main() 