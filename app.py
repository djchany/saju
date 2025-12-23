import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

st.set_page_config(page_title="지천명 AI 상담소", page_icon="🔮")

# 1. 시스템 프롬프트 (AI의 성격과 임무 정의)
SYSTEM_INSTRUCTION = """
당신은 대한민국 최고의 명리학자 '지천명'입니다. 사용자와 대화하며 사주를 봐주어야 합니다.
당신은 다음 정보를 모두 수집할 때까지는 사주 풀이를 시작하지 말고, 자연스럽게 대화하며 정보를 물어보세요.

[필요한 정보 목록]
1. 성함 (한자 포함 권장)
2. 생년월일 (양력/음력/윤달 여부 필수 확인)
3. 태어난 시간 (모르면 모른다고 해도 됨)
4. 성별

[대화 규칙]
- 사용자가 엉뚱한 소리를 하거나 정보를 제대로 주지 않으면, 명리학자답게 꾸짖거나 능청스럽게 다시 정보를 달라고 유도하세요.
- 예: "허허, 농담도 잘 하시는군. 하지만 생일을 알아야 천기를 읽을 수 있다네."
- 정보를 하나씩 물어봐도 되고, 한꺼번에 물어봐도 됩니다. 사용자의 말투에 맞춰 유연하게 대화하세요.
- 모든 정보(성함, 생년월일, 음양력, 시간, 성별)가 수집되었다고 판단되면, 그때 비로소 '사주 풀이'를 시작하세요.
"""

# 2. 세션 상태 초기화
if "chat_session" not in st.session_state:
    # 제미니의 대화 세션 시작
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", # 아까 성공한 모델
        system_instruction=SYSTEM_INSTRUCTION
    )
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.messages = []

# 3. UI 구성
st.title("🔮 지천명 AI 상담소")
st.caption("무엇이든 물어보시게. 사주를 보려면 먼저 통성명부터 해야겠지?")

# 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. 채팅 입력
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 저장 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # 제미니에게 메시지 전송 (이전 대화 맥락이 포함됨)
        response = st.session_state.chat_session.send_message(prompt)
        ai_response = response.text

        # AI 메시지 저장 및 표시
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        with st.chat_message("assistant"):
            st.markdown(ai_response)
            
    except Exception as e:
        st.error(f"오류가 발생했네: {e}")