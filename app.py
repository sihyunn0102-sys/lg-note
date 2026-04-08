import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 사이트 설정
st.set_page_config(page_title="LG인적성 AI 오답노트", layout="centered")

# Secrets에서 API 키 가져오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    # 통신 방식을 'rest'로 강제 지정하여 gRPC 404 오류 방지
    genai.configure(api_key=api_key, transport='rest')
except Exception:
    st.error("Secrets 설정에서 'GEMINI_API_KEY'를 확인해주세요.")
    st.stop()

st.title("🔋 LG Energy Solution 인적성 오답노트")

# [진단 기능] 현재 사용 가능한 모델 리스트 확인
with st.expander("🔍 내 API 키로 사용 가능한 모델 확인"):
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        st.write(available_models)
    except Exception as e:
        st.write("모델 리스트를 가져오지 못했습니다.")

# 2. 사용자 입력
category = st.selectbox("문제 영역", ["언어이해", "언어추리", "자료해석", "창의수리"])
uploaded_file = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="업로드된 이미지", use_container_width=True)

    if st.button("AI 오답 분석 시작"):
        with st.spinner("최적의 모델을 찾아 분석 중..."):
            
            # 시도할 모델 후보군 (최신 버전부터 순차적으로 시도)
            model_candidates = [
                'gemini-1.5-flash-latest', 
                'gemini-1.5-flash', 
                'gemini-1.5-pro',
                'models/gemini-1.5-flash'
            ]
            
            response_text = None
            success_model = None

            for model_name in model_candidates:
                try:
                    model = genai.GenerativeModel(model_name)
                    prompt = f"너는 LG그룹 인적성 전문가야. 영역은 {category}이야. 이 문제의 핵심 논리와 정확한 풀이를 알려줘."
                    response = model.generate_content([prompt, img])
                    response_text = response.text
                    success_model = model_name
                    break # 성공하면 루프 탈출
                except Exception:
                    continue # 실패하면 다음 모델로 시도

            if response_text:
                st.subheader(f"📝 AI 분석 결과 (연결 모델: {success_model})")
                st.write(response_text)
                st.success("분석 완료! 내용을 복사해 노션에 저장하세요.")
            else:
                st.error("모든 모델 연결에 실패했습니다. 구글 AI 스튜디오에서 API 키의 '결제 수단'이나 '사용 제한'을 확인해 보세요.")

st.caption("김시현님의 LG 합격과 하이닉스를 향한 도전을 응원합니다! 🚀")
