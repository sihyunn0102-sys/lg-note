import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import pandas as pd
from datetime import datetime
import requests
import base64
import io

st.set_page_config(page_title="시현님의 오답노트 치트키", layout="wide")

# ── API 연결 설정 ──────────────────────────────────────────────
try:
    GEMINI_API   = st.secrets["GEMINI_API_KEY"]
    NOTION_TOKEN = st.secrets.get("NOTION_TOKEN", "")
    NOTION_DB_ID = st.secrets.get("NOTION_DB_ID", "")
    IMGBB_API    = st.secrets.get("IMGBB_API_KEY", "")
    client = genai.Client(api_key=GEMINI_API)
except Exception:
    st.error("Secrets 설정을 확인해주세요.")
    st.stop()

# ── imgbb 이미지 업로드 ────────────────────────────────────────
def upload_image_to_imgbb(pil_image: Image.Image):
    if not IMGBB_API:
        return None
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    res = requests.post(
        "https://api.imgbb.com/1/upload",
        data={"key": IMGBB_API, "image": b64},
    )
    if res.status_code == 200:
        return res.json()["data"]["url"]
    return None

# ── 노션 페이지 생성 ───────────────────────────────────────────
def send_to_notion(category: str, filename: str, analysis: str, image_url):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    children = []

    if image_url:
        children.append({
            "object": "block",
            "type": "image",
            "image": {
                "type": "external",
                "external": {"url": image_url},
            },
        })

    children.append({
        "object": "block",
        "type": "toggle",
        "toggle": {
            "rich_text": [{"type": "text", "text": {"content": "💡 풀이 보기"}}],
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": analysis[:2000]}}
                        ]
                    },
                }
            ],
        },
    })

    data = {
        "parent": {"database_id": NOTION_DB_ID},
        "properties": {
            "영역": {"select": {"name": category}},
            "파일명": {"title": [{"text": {"content": filename}}]},
            "날짜": {"date": {"start": datetime.now().isoformat()}},
        },
        "children": children,
    }

    res = requests.post(url, headers=headers, json=data)
    return res.status_code == 200

# ── UI ────────────────────────────────────────────────────────
st.title("🔋 시현님의 인적성 합격 치트키")
st.caption("화공생물공학 전공의 강점을 살려 데이터로 오답을 정복하세요!")

category = st.selectbox(
    "영역 선택", ["언어이해", "언어추리", "자료해석", "창의수리"]
)
uploaded_files = st.file_uploader(
    "문제 캡처본 업로드", accept_multiple_files=True, type=["png", "jpg", "jpeg"]
)

if uploaded_files and st.button("일괄 분석 및 저장 시작"):
    for file in uploaded_files:
        with st.spinner(f"{file.name} 분석 중..."):
            img = Image.open(file)

            # PIL → bytes 변환
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            img_bytes = buf.getvalue()

            prompt = (
                f"이것은 LG 인적성 {category} 문제야. "
                "아래 형식으로 답해줘:\n"
                "1. 핵심 논리: (1줄)\n"
                "2. 정답: (번호 또는 값)\n"
                "3. 실수 방지 팁: (1줄)"
            )

            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[
                        prompt,
                        types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                    ],
                )
                analysis_txt = response.text

                # imgbb 업로드
                img_url = upload_image_to_imgbb(img)

                # 노션 전송
                notion_ok = False
                if NOTION_TOKEN and NOTION_DB_ID:
                    notion_ok = send_to_notion(category, file.name, analysis_txt, img_url)

                # 세션 히스토리
                if "history" not in st.session_state:
                    st.session_state.history = []
                st.session_state.history.append({
                    "영역": category,
                    "파일명": file.name,
                    "분석": analysis_txt,
                    "노션 전송": "✅" if notion_ok else "❌",
                })

                # 결과 표시
                with st.expander(f"📄 {file.name} 분석 결과", expanded=True):
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.image(img, width='stretch')
                    with col2:
                        st.markdown(analysis_txt)
                    st.caption(f"📬 노션 전송: {'✅ 성공' if notion_ok else '❌ 실패 (Secrets 또는 Integration 확인 필요)'}")

            except Exception as e:
                st.error(f"❌ {file.name} 오류: {e}")

# ── 히스토리 & 다운로드 ───────────────────────────────────────
if "history" in st.session_state and st.session_state.history:
    st.divider()
    st.subheader("📊 이번 세션 분석 내역")
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, width='stretch')
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 CSV로 내보내기",
        data=csv,
        file_name=f"LG_오답노트_{datetime.now().strftime('%Y%m%d')}.csv",
    )
