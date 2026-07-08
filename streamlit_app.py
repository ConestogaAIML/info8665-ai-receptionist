import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


st.set_page_config(page_title="AI Receptionist", page_icon="☎", layout="wide")
st.title("AI Receptionist")
st.caption("Log Management, Docker, and FAQ Knowledge Base Demo")


def api_url(path: str) -> str:
    return f"{API_BASE_URL.rstrip('/')}{path}"


@st.cache_data(ttl=30)
def get_token() -> str:
    response = requests.post(api_url("/auth/token?business_id=1"), timeout=10)
    response.raise_for_status()
    return response.json()["access_token"]


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {get_token()}"}


status_col, log_col = st.columns([1, 1])

with status_col:
    st.subheader("Application Status")
    try:
        response = requests.get(api_url("/"), timeout=10)
        response.raise_for_status()
        st.success(response.json()["message"])
        st.code(API_BASE_URL, language="text")
    except requests.RequestException as exc:
        st.error(f"API is not reachable: {exc}")

with log_col:
    st.subheader("Recent Log File Entries")
    try:
        response = requests.get(api_url("/logs/recent?limit=8"), timeout=10)
        response.raise_for_status()
        data = response.json()
        st.caption(f"Log file: {data['log_file']}")
        st.text("\n".join(data["lines"]) or "No log entries yet.")
    except requests.RequestException as exc:
        st.warning(f"Could not load logs: {exc}")


st.divider()
st.subheader("FAQ Knowledge Base")

with st.form("create_faq"):
    question = st.text_input("Question", "What are your business hours?")
    answer = st.text_area("Answer", "We are open Monday to Friday, 9 AM to 5 PM.")
    tags = st.text_input("Tags", "hours,general")
    submitted = st.form_submit_button("Create FAQ")

if submitted:
    payload = {
        "question": question,
        "answer": answer,
        "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
        "is_active": True,
    }
    try:
        response = requests.post(
            api_url("/api/faq/"),
            json=payload,
            headers=auth_headers(),
            timeout=10,
        )
        response.raise_for_status()
        st.success("FAQ item created.")
        st.json(response.json())
        st.cache_data.clear()
    except requests.RequestException as exc:
        st.error(f"FAQ creation failed: {exc}")

try:
    response = requests.get(api_url("/api/faq/"), headers=auth_headers(), timeout=10)
    response.raise_for_status()
    data = response.json()
    st.metric("FAQ Items", data["count"])
    st.dataframe(data["results"], use_container_width=True)
except requests.RequestException as exc:
    st.error(f"Could not load FAQ items: {exc}")

