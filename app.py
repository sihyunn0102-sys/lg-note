import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
from datetime import datetime
import requests # 노션 API 호출용

# 1. 설정 및 API 연결
st.set_page_config(page_title="LG/SK하이닉스 합격 오답노트", layout="wide")

# Secrets 설정 확인
try:
    GEMINI_API = st.secrets["GEMINI_API_KEY"]
    NOTION_TOKEN = st.secrets.get("NOTION_TOKEN", "")
    NOTION_DB_ID = st.secrets.get("NOTION_DB_ID", "")
    genai.configure(api_key=GEMINI_API, transport='rest')
except Exception:
    st.error("Secrets 설정을 확인해주세요 (GEMINI_API_KEY 필수)")
    st.stop()

# 노션 데이터 전송 함수
def send_to_notion(category, filename, analysis):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = {
        "parent": { "database_id": NOTION_DB_ID },
        "properties": {
            "영역": { "select": { "name": category } },
            "파일명": { "title": [{ "text": { "content": filename } }] },
            "분석내용": { "rich_text": [{ "text": { "content": analysis[:2000] } }] }, # 노션 글자수 제한 대응
            "날짜": { "date": { "start": datetime.now().isoformat() } }
        }
    }
    res = requests.post(url, headers=headers, json=data)
    return res.status_code == 200

st.title("🔋 시현님의 인적성 합격 치트키")
st.write(f"화공생물공학 전공의 강점을 살려 데이터로 오답을 정복하세요!")

# 2. 멀티 업로드 및 분석
category = st.selectbox("영역 선택", ["언어이해", "언어추리", "자료해석", "창의수리"])
uploaded_files = st.file_uploader("문제 캡처본 업로드", accept_multiple_files=True)

if uploaded_files:
    if st.button("일괄 분석 및 저장 시작"):
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        for file in uploaded_files:
            with st.spinner(f"{file.name} 분석 중..."):
                img = Image.open(file)
                prompt = f"{category} 문제야. 핵심논리/정답/실수방지 팁을 3줄로 요약해줘."
                
                try:
                    res = model.generate_content([prompt, img])
                    analysis_text = res.text
                    
                    # 노션 연동 (토큰이 있을 때만)
                    if NOTION_TOKEN and NOTION_DB_ID:
                        success = send_to_notion(category, file.name, analysis_text)
                        if success: st.success(f"✅ {file.name} 노션 저장 완료!")
                    
                    # 로컬 세션 DB 저장 (CSV용)
                    if 'history' not in st.session_state: st.session_state.history = []
                    st.session_state.history.append({
                        "영역": category, "파일명": file.name, "분석": analysis_text
                    })
                except Exception as e:
                    st.error(f"오류: {e}")

# 3. 엑셀(CSV) 추출기
if 'history' in st.session_state and st.session_state.history:
    st.divider()
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 엑셀(CSV)로 내보내기", data=csv, file_name="LG_오답노트.csv")
