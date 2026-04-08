import streamlit as st
from google import genai
from PIL import Image

# 1. 사이트 설정 및 API 키 연결
st.set_page_config(page_title="LG인적성 AI 오답노트", layout="centered")

# Secrets에서 키 가져오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("Secrets 설정에서 GEMINI_API_KEY를 확인해주세요.")
    st.stop()

st.title("🔋 LG Energy Solution 인적성 오답노트")
st.write("문항 캡처와 함께 나의 디지털 풀이를 올려주세요.")

# 2. 사용자 입력
category = st.selectbox("문제 영역", ["언어이해", "언어추리", "자료해석", "창의수리"])
uploaded_file = st.file_uploader("이미지 업로드 (PNG, JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="업로드된 문제 이미지", use_container_width=True)

    if st.button("AI 오답 분석 시작"):
        with st.spinner("LG 인적성 전문가 AI가 분석 중입니다..."):
            prompt = f"""
            너는 LG그룹 인적성 검사(LG Way Fit Test) 전문가야.
            업로드된 문제는 '{category}' 영역이야. 다음 항목에 맞춰 분석해줘.
            
            1. 문제 요약 및 핵심 규칙: 이 문제에서 반드시 파악해야 하는 논리가 뭐야?
            2. 정답 및 풀이 과정: 단계별로 정확한 풀이를 알려줘.
            3. 디지털 도구 활용 팁: LG 인적성은 메모장과 계산기만 쓸 수 있어. 이 도구들을 써서 어떻게 하면 더 빠르고 정확하게 풀 수 있을까?
            4. 함정 포인트: 사람들이 흔히 실수하는 부분은 뭐야?
            """
            
            try:
                # 최신 라이브러리 방식 호출
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=[prompt, img]
                )
                
                st.subheader("📝 AI 분석 결과")
                st.write(response.text)
                
                st.divider()
                st.info("이 내용을 복사해서 노션 오답노트에 붙여넣으세요!")
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

st.caption("김시현님의 LG 합격을 응원합니다! (Final Goal: SK Hynix)")
