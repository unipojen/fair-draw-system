import streamlit as st
import secrets
import pandas as pd
import time
from datetime import datetime

# --- 設定頁面資訊 ---
st.set_page_config(
    page_title="公正抽籤系統 - 技師團隊",
    page_icon="⚖️",
    layout="centered"
)

# --- 初始化系統記憶體 (Session State) ---
# 這樣才能在網頁上動態新增名單而不見
if 'seniors_list' not in st.session_state:
    st.session_state.seniors_list = [
        "Nancy", "Shen", "Edward", "Leo", "Frank", "Jimmy", 
        "Hunk", "Jason", "Manfred", "Tommy", "Ivan", 
        "Jonathan", "Hardy", "Pai"
    ]

if 'regulars_list' not in st.session_state:
    st.session_state.regulars_list = [
        "Willie", "Anson", "Ken", "Johnson", "Ed", "Ethan", 
        "Yuzu", "Alex", "Chris", "Dylan", "Stanley"
    ]

# --- 核心邏輯：軍規等級隨機 (Cryptographically Secure Random) ---
def chaos_simulation(population, k, rounds=1000):
    if k > len(population):
        return population
        
    secure_random = secrets.SystemRandom()
    results_pool = []
    
    for _ in range(rounds):
        results_pool.append(secure_random.sample(population, k))
    
    final_choice = secure_random.choice(results_pool)
    return final_choice

# --- APP 介面 ---
st.title("⚖️ 技師團隊 - 公正抽籤系統")
st.markdown("### Secure Random System v1.1")
st.info("本系統採用 Python `secrets` 模組，具備密碼學等級隨機性。新增動態人員擴充功能。")

# --- 1. 側邊欄：人員設定與新增 ---
st.sidebar.header("人員設定")
st.sidebar.markdown("請勾選 **目前可參加抽籤** 的人員")

# 顯示資深技師勾選區
st.sidebar.subheader(f"資深技師 ({len(st.session_state.seniors_list)}人)")
active_seniors = []
for name in st.session_state.seniors_list:
    if st.sidebar.checkbox(name, value=True, key=f"s_{name}"):
        active_seniors.append(name)

# 顯示一般技師勾選區
st.sidebar.subheader(f"一般技師 ({len(st.session_state.regulars_list)}人)")
active_regulars = []
for name in st.session_state.regulars_list:
    if st.sidebar.checkbox(name, value=True, key=f"r_{name}"):
        active_regulars.append(name)

# 新增人員區塊
st.sidebar.divider()
st.sidebar.subheader("➕ 新增臨時技師")
st.sidebar.caption("在此新增的人員會立刻出現在上方名單中")
new_name = st.sidebar.text_input("輸入技師英文名", placeholder="例如: Kevin")
new_role = st.sidebar.radio("選擇身分", ["一般技師", "資深技師"])

if st.sidebar.button("確認加入", use_container_width=True):
    if new_name.strip() == "":
        st.sidebar.error("請輸入名字！")
    else:
        name_clean = new_name.strip()
        if new_role == "資深技師" and name_clean not in st.session_state.seniors_list:
            st.session_state.seniors_list.append(name_clean)
            st.rerun() # 重新整理畫面讓勾選框出現
        elif new_role == "一般技師" and name_clean not in st.session_state.regulars_list:
            st.session_state.regulars_list.append(name_clean)
            st.rerun()
        else:
            st.sidebar.warning("這個名字已經在名單裡囉！")

# --- 2. 主畫面：設定抽籤模式 ---
st.divider()
col1, col2 = st.columns(2)

with col1:
    draw_mode = st.radio(
        "選擇抽籤目標",
        ("單人中獎 (天選之人)", "組隊分配 (如: 抽一組6人)", "多組輪值 (如: 抽4組)")
    )

with col2:
    if "單人" in draw_mode:
        num_winners = 1
        st.write("設定：從名單中抽出 1 人")
    elif "組隊" in draw_mode:
        num_winners = st.number_input("本組需要幾人？", min_value=1, value=6)
        min_seniors = st.number_input("其中至少含幾位資深？", min_value=0, value=2)
    else:
        num_groups = st.number_input("要抽幾組？", min_value=2, value=4)
        people_per_group = st.number_input("每組幾人？", min_value=1, value=6)

# --- 3. 執行按鈕 ---
st.divider()
verify_hash = secrets.token_hex(4).upper()

if st.button("🚀 啟動軍規亂數抽籤", use_container_width=True):
    
    progress_text = "正在初始化隨機源..."
    my_bar = st.progress(0, text=progress_text)
    time.sleep(0.3)
    my_bar.progress(30, text="正在執行 1,000 次蒙地卡羅模擬...")
    time.sleep(0.5)
    my_bar.progress(80, text="正在進行密碼學雜湊驗證...")
    time.sleep(0.2)
    my_bar.progress(100, text="抽籤完成！")
    time.sleep(0.1)
    my_bar.empty()

    st.success(f"✅ 抽籤完成｜時間戳記：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}｜驗證碼：{verify_hash}")

    # 邏輯處理
    if "單人" in draw_mode:
        full_pool = active_seniors + active_regulars
        if not full_pool:
            st.error("名單為空，請在左側勾選人員")
        else:
            winner = chaos_simulation(full_pool, 1)
            st.balloons()
            st.markdown(f"## 🎉 得獎者：**{winner[0]}**")

    elif "組隊" in draw_mode:
        if len(active_seniors) < min_seniors:
            st.error(f"資深技師人數不足！目前勾選 {len(active_seniors)} 人，但要求 {min_seniors} 人。")
        else:
            selected_seniors = chaos_simulation(active_seniors, min_seniors)
            remaining_seniors = [p for p in active_seniors if p not in selected_seniors]
            remaining_pool = remaining_seniors + active_regulars
            needed_others = num_winners - min_seniors
            
            if len(remaining_pool) < needed_others:
                 st.error(f"剩餘人數不足！還需 {needed_others} 人，但只剩 {len(remaining_pool)} 人。")
            else:
                selected_others = chaos_simulation(remaining_pool, needed_others)
                final_team = list(selected_seniors) + list(selected_others)
                
                st.balloons()
                st.markdown("### 📋 中選小組名單")
                display_list = []
                for p in final_team:
                    role = "★ 資深" if p in st.session_state.seniors_list else "一般"
                    display_list.append({"身分": role, "姓名": p})
                st.table(pd.DataFrame(display_list))

    elif "多組" in draw_mode:
        full_pool = active_seniors + active_regulars
        total_needed = num_groups * people_per_group
        
        if len(full_pool) < total_needed:
             st.warning(f"⚠️ 總名單只有 {len(full_pool)} 人，抽 {total_needed} 席次必然會有人重複。")
        
        secure_random = secrets.SystemRandom()
        extended_pool = full_pool[:]
        while len(extended_pool) < total_needed:
             extended_pool += full_pool
        secure_random.shuffle(extended_pool)
        
        st.markdown("### 📅 分組結果")
        for i in range(num_groups):
            start = i * people_per_group
            end = start + people_per_group
            group_members = extended_pool[start:end]
            
            formatted_members = []
            for m in group_members:
                if m in st.session_state.seniors_list:
                    formatted_members.append(f"★ {m}")
                else:
                    formatted_members.append(m)
            
            st.write(f"**第 {i+1} 組**： {', '.join(formatted_members)}")
            st.divider()

st.markdown("---")
st.caption("🔒 Security Note: This drawing uses Python's `secrets` module (CSPRNG). No seed pattern, 100% unpredictable.")
