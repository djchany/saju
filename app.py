import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime
from dotenv import load_dotenv

# 1. 환경 설정 및 API 키 로드
load_dotenv()

def get_api_key():
    # 1. 먼저 로컬 .env 파일이나 환경 변수에서 찾아봅니다 (가장 안전)
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        return api_key

    # 2. 환경 변수에 없다면 Streamlit Secrets 시도 (에러 방지를 위해 try-except 사용)
    try:
        if hasattr(st, "secrets") and "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        pass # Secrets 파일이 없어도 에러를 내지 않고 넘어갑니다.

    return None

api_key = get_api_key()

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API 키를 찾을 수 없습니다. Secrets 설정이나 .env 파일을 확인해주세요.")
    st.stop()

# 2. 페이지 설정 및 디자인
st.set_page_config(page_title="지천명 종합 운세 상담소", page_icon="🔮", layout="wide")

# 카카오톡 느낌을 위한 커스텀 CSS
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .stChatInputContainer { padding-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 카테고리 데이터 정의
CATEGORIES = {
    "정통운세": ["월간 종합운세", "평생운세", "2026년 신토정비결", "2026 부자되기"],
    "생활운세": ["오늘의 운세", "주간 종합운세", "프리미엄 로또운세"],
    "애정/궁합": ["내사랑 반쪽찾기", "내 운명의 배우자", "프리미엄 궁합"]
}

# 4. 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "current_sub" not in st.session_state:
    st.session_state.current_sub = None

# --- 사이드바: 카테고리 선택 ---
with st.sidebar:
    st.title("📜 운세 카테고리")
    main_cat = st.selectbox("큰 분류를 선택하게", list(CATEGORIES.keys()))
    sub_cat = st.radio("상세 운세를 고르시게", CATEGORIES[main_cat])
    
    st.divider()
    if st.button("🔄 새로운 상담 시작", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.session_state.current_sub = sub_cat
        st.rerun()

# --- 메인 화면 로직 ---

# 현재 날짜 및 시간 정보 (AI에게 주입용)
now = datetime.now()
curr_date_str = now.strftime("%Y년 %m월 %d일 %H시 %M분")

# 시스템 프롬프트 설정
SYSTEM_INSTRUCTION = f"""
당신은 대한민국 최고의 명리학 대가 '지천명'입니다.
현재 시각은 {curr_date_str} (요일 포함) 입니다. 모든 답변은 이 시점을 기준으로 작성하세요.

현재 사용자가 선택한 서비스는 [{sub_cat}] 입니다.

[필수 수집 정보]
1. 이름 (한자 포함 가능)
2. 성별
3. 생년월일 (양력/음력/평달/윤달 여부)
4. 태어난 시간 (모르면 모른다고 해도 됨)

[특수 규칙]
- 사용자가 '프리미엄 궁합'을 선택했다면, 반드시 상대방의 이름, 성별, 생년월일, 태어난 시간 정보도 함께 물어보세요.
- 정보가 수집되기 전에는 절대로 사주 풀이를 시작하지 마세요.
- 정보가 틀리거나 엉뚱한 말을 하면 명리학자답게 능청스럽게 다시 물어보세요.
- 말투는 "~하시게", "~로군", "~인가?" 같은 고풍스러운 말투를 유지하세요.
- 모든 정보가 수집되면 [{sub_cat}]의 성격에 맞춰 전문적인 역학 분석을 제공하세요.
"""

# AI 세션 초기화
if st.session_state.chat_session is None or st.session_state.current_sub != sub_cat:
    st.session_state.current_sub = sub_cat
    model = genai.GenerativeModel(
        model_name="models/gemini-2.5-flash", # 안정적인 모델 사용
        system_instruction=SYSTEM_INSTRUCTION
    )
    st.session_state.chat_session = model.start_chat(history=[])
    
    # 첫 인사 메시지
    welcome_msg = f"어서오게. [{sub_cat}]을 보러 왔는가? 사주 명반을 펼치기 전에 자네의 통성명과 생년월일시부터 차근차근 알려주시게."
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]

# 화면 표시
st.title(f"🔮 {sub_cat}")
st.caption(f"기준 시각: {curr_date_str} | 상담가: 지천명")

# 대화 기록 렌더링
for message in st.session_state.messages:
    avatar = "🔮" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 채팅 입력창
if prompt := st.chat_input("답변을 입력하세요..."):
    # 사용자 메시지 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # AI 응답 생성
    try:
        response = st.session_state.chat_session.send_message(prompt)
        ai_response = response.text
        
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        with st.chat_message("assistant", avatar="🔮"):
            st.markdown(ai_response)
    except Exception as e:
        st.error(f"지천명 선생이 잠시 자리를 비웠네(오류): {e}")