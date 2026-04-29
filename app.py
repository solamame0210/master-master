import streamlit as st
import random
import math
import time
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

if "submitted" not in st.session_state:
    st.session_state.submitted = False

# =========================
# Google Sheets 接続
# =========================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope
)

client = gspread.authorize(creds)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1I9Q2qB99pqfoof0KtssyNJgcuW4xIaFatfysVEvFdVA/edit?gid=0#gid=0").sheet1
def save_score(name, score):
    sheet.append_row([name, score])

def get_ranking():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df.sort_values("時間(s)")

# =========================
# ゲーム部分
# =========================
if "round" not in st.session_state:
    st.session_state.round = 0
    st.session_state.total_time = 0
    st.session_state.start_time = 0
    st.session_state.value = 0
    st.session_state.answer = ""
    st.session_state.finished = False

n = [0.125,0.25,0.5,1,2,4,8,16,32,64]

def generate_question():
    a = [1]
    for _ in range(3):
        a.append(random.randint(0,1))

    f = float(random.choice(n))

    t = 0
    for j in range(len(a)):
        t += a[j] * f / (2**j)

    o = format((127 + int(math.log2(f))), '08b')

    del a[0]
    for y in range(len(a)):
        o += str(a[y])

    return t, o

st.markdown("<h1 style='text-align: center;'>浮動小数点マスターマスター</h1>", unsafe_allow_html=True)

# スタート
if st.button("スタート"):
    st.session_state.round = 1
    st.session_state.total_time = 0
    st.session_state.finished = False
    st.session_state.value, st.session_state.answer = generate_question()
    st.session_state.start_time = time.time()

# ゲーム
if 1 <= st.session_state.round <= 3:
    st.subheader(f"第 {st.session_state.round} 問")
    st.write("値:", st.session_state.value)

    with st.form(key="quiz_form", clear_on_submit=True):
        user_input = st.text_input("指数部８桁＋仮数部３桁を入力")
        submitted = st.form_submit_button("送信")

    if submitted:
        if user_input == st.session_state.answer:
            elapsed = time.time() - st.session_state.start_time
            st.session_state.total_time += elapsed

            st.success(f"正解！ {elapsed:.2f}秒")

            st.session_state.round += 1

            if st.session_state.round <= 3:
                st.session_state.value, st.session_state.answer = generate_question()
                st.session_state.start_time = time.time()
                st.rerun()
            else:
                st.session_state.finished = True
        else:
            st.error("不正解")
# 終了
if st.session_state.finished:
    total = int(st.session_state.total_time)

    st.title("終了")
    st.write(f"合計時間: {total} 秒")

    name = st.text_input("名前を入力")

    if not st.session_state.submitted:
        if st.button("ランキング登録"):
            if name.strip() != "":
                save_score(name, total)
                st.success("登録完了")
                st.session_state.submitted = True  
            else:
                st.warning("名前を入力")
    else:
        st.info("すでに登録済みです")

st.subheader("ランキング")

df = get_ranking()

df = df.reset_index(drop=True)
df.insert(0, "順位", df.index + 1)

st.markdown("""
<style>
/* 表全体 */
table {
    width: 50% !important;
    margin-left: auto;
    margin-right: auto;
}

/* 1列目（順位）を小さく */
th:nth-child(1), td:nth-child(1) {
    width: 50px !important;
    text-align: center;
}

/* 他の列は中央 */
th, td {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)
st.table(df.head(10))
