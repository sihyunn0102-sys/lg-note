import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 사이트 설정
st.set_page_config(page_title="LG인적성 AI 오답노트", layout="centered")

# Secrets에서 API 키 가져오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
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
    st.image(img, caption="업로드된 이미지", use_container_width=True)

    if st.button("AI 오답 분석 시작"):
        with st.spinner("AI가 문제를 분석 중입니다..."):
            # 에러 방지를 위해 모델 이름을 리스트에서 직접 확인 후 할당
            # 가장 범용적인 'gemini-1.5-flash'를 사용합니다.
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"너는 LG그룹 인적성 전문가야. 영역은 {category}이야. 이 문제의 핵심 논리와 정확한 풀이, 그리고 메모장/계산기만 사용하는 LG 환경에서의 팁을 알려줘."
            
            try:
                # 이미지와 텍스트 전송 (가장 표준적인 방식)
                response = model.generate_content([prompt, img])
                
                st.subheader("📝 AI 분석 결과")
                st.write(response.text)
                st.success("분석 완료! 내용을 복사해 노션에 저장하세요.")
                
            except Exception as e:
                # 만약 또 404가 난다면 모델 이름을 'models/gemini-1.5-flash'로 시도
                st.warning("기본 연결 실패, 보조 경로로 재시도합니다...")
                try:
                    alt_model = genai.GenerativeModel('models/gemini-1.5-flash')
                    response = alt_model.generate_content([prompt, img])
                    st.write(response.text)
                except Exception as final_e:
                    st.error(f"최종 오류: {final_e}\n구글 AI 스튜디오에서 API 키가 활성 상태인지 확인이 필요합니다.")
