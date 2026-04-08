import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 사이트 및 API 설정
st.set_page_config(page_title="LG인적성 AI 오답노트", layout="centered")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    # 통신 방식을 'rest'로 지정하여 Streamlit 서버의 gRPC 404 에러를 원천 차단합니다.
    genai.configure(api_key=api_key, transport='rest')
except Exception:
    st.error("Secrets 설정에서 'GEMINI_API_KEY'를 확인해주세요.")
    st.stop()

st.title("🔋 LG Energy Solution 인적성 오답노트")
st.write("문항 캡처를 올려주시면 LG 인적성 전문가 AI가 분석해 드립니다.")

# 2. 사용자 입력
category = st.selectbox("문제 영역", ["언어이해", "언어추리", "자료해석", "창의수리"])
uploaded_file = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="업로드된 문제", use_container_width=True)

    if st.button("AI 오답 분석 시작"):
        with st.spinner("최신 Gemini 3 모델로 분석 중..."): # 현재 모델은 Gemini 3 Flash입니다. 
            try:
                # 시현님 리스트에서 확인된 최신 모델 이름을 직접 사용합니다.
                model = genai.GenerativeModel('gemini-3-flash-preview')
                
                prompt = f"""
                너는 LG그룹 인적성 전문가야. 영역은 {category}이야.
                이미지 속 문제를 분석해서 '핵심 논리', '단계별 풀이', 'LG 환경(메모장/계산기) 최적 팁'을 알려줘.
                """
                
                response = model.generate_content([prompt, img])
                
                st.subheader("📝 AI 분석 결과")
                st.write(response.text)
                st.success("분석이 완료되었습니다!")
                
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
                st.info("로컬 테스트에서는 성공했으므로, 잠시 후 다시 시도해보세요.")

st.caption("🦖🦕🦖🦕🦖🦕🦖🦕💙💙🚀")
