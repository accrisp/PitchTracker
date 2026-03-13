import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(page_title="Coach's Pitch Tracker", layout="wide")

# Initialize Session State to store roster data
if 'pitch_data' not in st.session_state:
    st.session_state.pitch_data = pd.DataFrame(columns=[
        "Date", "Player", "Grade", "Innings", "Total Pitches", "Next Available"
    ])

# --- LOGIC FUNCTIONS ---
def get_max_pitches(grade):
    limits = {"7-8": 85, "9-10": 100, "11-12": 120}
    return limits.get(grade, 85)

def calculate_rest_date(pitches, game_date):
    if pitches <= 25:
        days_rest = 1
    elif pitches <= 50:
        days_rest = 2
    elif pitches <= 75:
        days_rest = 3
    else:
        days_rest = 4
    return game_date + timedelta(days=days_rest)

# --- SIDEBAR: INPUT ---
st.sidebar.header("⚾ Log New Pitch Count")
with st.sidebar.form("pitch_form", clear_on_submit=True):
    p_name = st.text_input("Player Name")
    p_grade = st.selectbox("Grade Level", ["7-8", "9-10", "11-12"])
    g_date = st.date_input("Game Date", datetime.now())
    
    col_a, col_b = st.columns(2)
    p_innings = col_a.number_input("Innings", min_value=0.1, step=0.1)
    p_total = col_b.number_input("Total Pitches", min_value=0, step=1)
    
    submit = st.form_submit_button("Save Pitch Data")

if submit and p_name:
    max_allowed = get_max_pitches(p_grade)
    if p_total > max_allowed:
        st.error(f"⚠️ Alert: {p_name} exceeded the {max_allowed} pitch limit for their grade!")
    
    next_date = calculate_rest_date(p_total, g_date)
    
    new_entry = {
        "Date": g_date,
        "Player": p_name,
        "Grade": p_grade,
        "Innings": p_innings,
        "Total Pitches": p_total,
        "Next Available": next_date
    }
    st.session_state.pitch_data = pd.concat([st.session_state.pitch_data, pd.DataFrame([new_entry])], ignore_index=True)
    st.success(f"Saved! {p_name} is available on {next_date.strftime('%Y-%m-%d')}")

# --- MAIN PAGE TABS ---
tab1, tab2, tab3 = st.tabs(["🔴 Unavailable List", "📊 Season Data", "📥 Export & Admin"])

with tab1:
    st.subheader("Players Currently Resting")
    today = datetime.now().date()
    unavailable = st.session_state.pitch_data[st.session_state.pitch_data["Next Available"] > today]
    
    if not unavailable.empty:
        # Show only the latest entry per player for clarity
        latest_unavailable = unavailable.sort_values("Date").groupby("Player").last()
        st.table(latest_unavailable[["Date", "Total Pitches", "Next Available"]])
    else:
        st.info("All players are currently available to pitch.")

with tab2:
    st.subheader("Full Season Roster Stats")
    search = st.text_input("Search Player Name")
    df_display = st.session_state.pitch_data
    if search:
        df_display = df_display[df_display["Player"].str.contains(search, case=False)]
    
    st.dataframe(df_display, use_container_width=True)

with tab3:
    st.subheader("Data Management")
    csv = st.session_state.pitch_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Full Season CSV",
        data=csv,
        file_name=f"pitch_logs_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv',
    )
    
    if st.button("Clear All Data"):
        st.session_state.pitch_data = pd.DataFrame(columns=["Date", "Player", "Grade", "Innings", "Total Pitches", "Next Available"])
        st.rerun()