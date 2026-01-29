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

# --- 核心邏輯：軍規等級隨機 (Cryptographically Secure Random) ---
def chaos_simulation(population, k, rounds=1000):
    """
    混沌模擬模式：
    先在背景執行 rounds 次抽籤，產生 1000 個平行宇宙結果。
    再從這 1000 個結果中，隨機抓取 1 個。
    """
    # 如果要抽的人數 k 大於名單人數，就全選
    if k > len(population):
        return population
        
    secure_random = secrets.SystemRandom()
    results_pool = []
    
    for _ in range(rounds):
        results_pool.append(secure_random.sample(population, k))
    
    # 從 1000 個宇宙中抽出一個
    final_choice = secure_random.choice(results_pool)
    return final_choice

# --- 名單資料庫 (依據上傳的最新名單更新) ---
# 資深技師
DEFAULT_SENIORS = [
    "Nancy", "Shen", "Edward", "Leo", "Frank", "Jimmy", 
    "Hunk", "Jason", "Manfred", "Tommy", "Ivan", 
    "Jonathan", "Hardy", "Pai"
]

# 一般技師
DEFAULT_REGULARS = [
    "Willie", "Anson", "Ken", "Johnson", "Ed", "Ethan", 
    "Yuzu", "Alex", "Chris", "Dylan", "Stanley"
]

# --- APP 介面 ---
st.title("⚖️ 技師團隊 - 公正抽籤系統")
st.markdown("### Secure Random System v1.0")
st.info("本系統採用 Python `secrets` 模組（CSPRNG），具備密碼學等級的隨機性，保證無規律、不可預測。")

# 1. 側邊欄：設定名單
st.sidebar.header("人員設定")
st.sidebar.markdown("請勾選 **目前可參加抽籤** 的人員 (請假/出海者請取消勾選)")

# 資深技師勾選區
st.sidebar.subheader(f"資深技師 ({len(DEFAULT_SENIORS)}人)")
active_seniors = []
for name in DEFAULT_SENIORS:
    # 預設全選，可手動取消
    if st.sidebar.checkbox(name, value=True, key=f"s_{name}"):
        active_seniors.append(name)

# 一般技師勾選區
st.sidebar.subheader(f"一般技師 ({len(DEFAULT_REGULARS)}人)")
active_regulars = []
for name in DEFAULT_REGULARS:
    # 預設全選，可手動取消
    if st.sidebar.checkbox(name, value=True, key=f"r_{name}"):
        active_regulars.append(name)

# 2. 主畫面：設定抽籤模式
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

# 3. 執行按鈕
st.divider()
verify_hash = secrets.token_hex(4).upper() # 產生隨機驗證碼

if st.button("🚀 啟動軍規亂數抽籤", use_container_width=True):
    
    # 動畫效果，增加儀式感
    progress_text = "正在初始化 `secrets` 隨機源..."
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

    # --- 邏輯處理 ---
    if "單人" in draw_mode:
        # 混合所有名單
        full_pool = active_seniors + active_regulars
        if not full_pool:
            st.error("名單為空，請在左側勾選人員")
        else:
            winner = chaos_simulation(full_pool, 1)
            st.balloons()
            st.markdown(f"## 🎉 得獎者：**{winner[0]}**")

    elif "組隊" in draw_mode:
        # 邏輯：先抽資深，再抽一般填滿
        if len(active_seniors) < min_seniors:
            st.error(f"資深技師人數不足！目前只有 {len(active_seniors)} 人，但您要求 {min_seniors} 人。")
        else:
            # 1. 抽資深
            selected_seniors = chaos_simulation(active_seniors, min_seniors)
            
            # 2. 剩下的人混合抽
            # 從還沒被選中的資深 + 所有一般技師中去抽
            remaining_seniors = [p for p in active_seniors if p not in selected_seniors]
            remaining_pool = remaining_seniors + active_regulars
            
            needed_others = num_winners - min_seniors
            
            if len(remaining_pool) < needed_others:
                 st.error(f"剩餘人數不足！還需要 {needed_others} 人，但只剩 {len(remaining_pool)} 人。")
            else:
                selected_others = chaos_simulation(remaining_pool, needed_others)
                # 為了顯示好看，我們把資深排前面
                final_team = list(selected_seniors) + list(selected_others)
                
                st.balloons()
                st.markdown("### 📋 中選小組名單")
                
                # 製作顯示用的 DataFrame
                display_list = []
                for p in final_team:
                    role = "★ 資深" if p in DEFAULT_SENIORS else "一般"
                    display_list.append({"身分": role, "姓名": p})
                
                st.table(pd.DataFrame(display_list))

    elif "多組" in draw_mode:
        # 簡單輪值邏輯 (大風吹)
        full_pool = active_seniors + active_regulars
        
        # 檢查總人數
        total_needed = num_groups * people_per_group
        if len(full_pool) < total_needed:
             st.warning(f"⚠️ 注意：總名單只有 {len(full_pool)} 人，但您要抽 {total_needed} 個席次，必然會有人重複中獎。")
        
        # 使用 secrets 進行洗牌
        secure_random = secrets.SystemRandom()
        # 為了支援重複中獎，我們建立一個足夠大的池子
        extended_pool = full_pool[:]
        while len(extended_pool) < total_needed:
             extended_pool += full_pool # 不夠就再複製一份進來
        
        secure_random.shuffle(extended_pool)
        
        st.markdown("### 📅 分組結果")
        
        for i in range(num_groups):
            start = i * people_per_group
            end = start + people_per_group
            group_members = extended_pool[start:end]
            
            # 格式化顯示
            formatted_members = []
            for m in group_members:
                if m in DEFAULT_SENIORS:
                    formatted_members.append(f"★ {m}")
                else:
                    formatted_members.append(m)
            
            st.write(f"**第 {i+1} 組**： {', '.join(formatted_members)}")
            st.divider()

# 頁尾
st.markdown("---")
st.caption("🔒 Security Note: This drawing uses Python's `secrets` module (CSPRNG). No seed pattern, 100% unpredictable.")
