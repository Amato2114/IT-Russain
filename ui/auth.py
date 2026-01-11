import streamlit as st
import os
import csv
from datetime import datetime

LOG_FILE = "logs/login_log.csv"

def log_login(login: str, status: str):
    os.makedirs("logs", exist_ok=True)
    ip = st.context.headers.get("X-Forwarded-For", "unknown").split(",")[0].strip()
    row = [login, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ip, status]
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["login", "timestamp", "ip", "status"])
        writer.writerow(row)

def login_form():
    st.header("🔐 Вход в систему")
    login = st.text_input("Логин")
    password = st.text_input("Пароль", type="password")
    if st.button("Войти"):
        users = st.secrets.get("auth", {}).get("users", [])
        for user in users:
            if user["login"] == login and user["password"] == password:
                log_login(login, "success")
                st.session_state["user"] = login
                st.success("✅ Успешный вход")
                st.rerun()
                return
        log_login(login, "fail")
        st.error("❌ Неверный логин или пароль")

def logout():
    if st.sidebar.button("🚪 Выйти"):
        st.session_state.pop("user", None)
        st.rerun()

def sidebar_auth_and_upload():
    if "user" not in st.session_state:
        login_form()
        st.stop()

    st.sidebar.success(f"👤 {st.session_state['user']}")
    logout()

    st.sidebar.header("📤 Данные")
    uploaded_file = st.sidebar.file_uploader("Загрузите Excel-файл", type=["xlsx", "xls"])
    use_test_data = False
    if st.sidebar.button("🧪 Тестовые данные (300 строк)"):
        use_test_data = True
    return uploaded_file, use_test_data