import streamlit as st
from google import genai  # 최신 SDK 사용
from PIL import Image

# 1. 사이트 설정
st.set_page_config(page_title="LG인적성 AI 오답노트", layout="centered")

# Secrets에서 API 키 가져오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key) # 최신 방식의 클라이언트 생성
except Exception:
    st.error("Streamlit Secrets에 'GEMINI_API_KEY'가 설정되어 있는지 확인해주세요.")
    st.stop()

st.title("🔋 LG Energy Solution 인적성 오답노트")
st.write("문항 캡처와 나의 풀이를 올려주시면 AI가 분석해 드립니다.")

# 2. 영역 선택 및 이미지 업로드
category = st.selectbox("문제 영역", ["언어이해", "언어추리", "자료해석", "창의수리"])
uploaded_file = st.file_uploader("문제 이미지 업로드", type=["png", "jpg", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="업로드된 이미지", use_container_width=True)

    if st.button("AI 오답 분석 시작"):
        with st.spinner("LG 인적성 전문가 AI가 분석 중입니다..."):
            prompt = f"""
            너는 LG그룹 인적성 전문가야. 
            영역: {category}
            위 이미지 속 문제를 분석해서 다음 내용을 알려줘:
            1. 핵심 논리/규칙
            2. 정답 및 단계별 풀이
            3. LG 인적성 환경(메모장/계산기만 사용 가능)에서의 효율적인 풀이 팁
            """
            
            try:
                # 모델 명칭을 'gemini-2.0-flash'로 시도 (404 방지)
                response = client.models.generate_content(
                    model="gemini-2.0-flash", 
                    contents=[prompt, img]
                )
                
                st.subheader("📝 AI 분석 결과")
                st.write(response.text)
                st.info("이 내용을 복사해서 노션 오답노트에 붙여넣으세요!")
                
            except Exception as e:
                # 만약 2.0도 안 된다면 1.5-flash로 재시도하는 로직
                st.warning("모델 연결 시도 중... 다시 한번 확인합니다.")
                try:
                    response = client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=[prompt, img]
                    )
                    st.write(response.text)
                except Exception as final_e:
                    st.error(f"최종 오류 발생: {final_e}")

