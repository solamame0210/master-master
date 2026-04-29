import streamlit as st
import random
import math
import time
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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
sheet = client.open("ランキング").sheet1

def save_score(name, score):
    sheet.append_row([name, score])

def get_ranking():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df.sort_values("時間")

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

st.title("浮動小数点マスター（オンラインランキング）")

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

    user_input = st.text_input("2進数を入力")

    if st.button("決定"):
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

    st.title("終了！")
    st.write(f"合計時間: {total} 秒")

    name = st.text_input("名前を入力")

    if st.button("ランキング登録"):
        if name.strip() != "":
            save_score(name, total)
            st.success("登録完了！")
        else:
            st.warning("名前を入力して！")

    st.subheader("ランキング")
    df = get_ranking()
    st.dataframe(df.head(10))
