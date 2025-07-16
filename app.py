import streamlit as st
import pandas as pd
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# ---------- CONFIGURATION ----------
SHEET_NAME = "FitSheet"
WORKOUT_SHEET = "Workout Log"
METRICS_SHEET = "Body Metrics"
CREDS_FILE = "service_account.json"

# ---------- GOOGLE SHEETS SETUP ----------
@st.cache_resource
def init_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    st.write("🔐 Starting credential loading...")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp"]), scope)
    st.write("✅ Credentials loaded, authorizing gspread...")
    client = gspread.authorize(creds)
    st.write("📄 Gspread client initialized")  # Final checkpoint
    return client

def log_workout(date, exercise, sets, reps, weight):
    client = init_gsheet()
    sheet = client.open(SHEET_NAME).worksheet(WORKOUT_SHEET)
    row = [str(date), exercise, sets, reps, weight]
    sheet.append_row(row)

def log_metrics(date, body_weight, body_fat, muscle_mass, fat_mass):
    client = init_gsheet()
    sheet = client.open(SHEET_NAME).worksheet(METRICS_SHEET)
    row = [str(date), body_weight, body_fat, muscle_mass, fat_mass]
    sheet.append_row(row)

def show_data_preview():
    st.header("📜 Workout & Progress History")
    client = init_gsheet()

    try:
        # --- Workout Log ---
        workout_data = client.open(SHEET_NAME).worksheet(WORKOUT_SHEET).get_all_records()
        if workout_data:
            workout_df = pd.DataFrame(workout_data)
            workout_df["Date"] = pd.to_datetime(workout_df["Date"])
            workout_df = workout_df.sort_values("Date", ascending=False)
            st.subheader("🏋️ Workout Log")
            st.dataframe(workout_df, use_container_width=True)
        else:
            st.info("No workout logs yet.")

        # --- Body Metrics ---
        metrics_data = client.open(SHEET_NAME).worksheet(METRICS_SHEET).get_all_records()
        if metrics_data:
            metrics_df = pd.DataFrame(metrics_data)
            metrics_df["Date"] = pd.to_datetime(metrics_df["Date"])
            metrics_df = metrics_df.sort_values("Date", ascending=False)
            st.subheader("📈 Body Metrics Log")
            st.dataframe(metrics_df, use_container_width=True)
        else:
            st.info("No body metrics logged yet.")

    except Exception as e:
        st.error(f"❌ Failed to load history: {e}")

def show_progress_charts():
    st.header("📉 Visualize Progress")

    client = init_gsheet()
    try:
        # Get Body Metrics
        metrics_data = client.open(SHEET_NAME).worksheet(METRICS_SHEET).get_all_records()
        if not metrics_data:
            st.info("No body metrics data to plot.")
            return

        df = pd.DataFrame(metrics_data)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        st.subheader("📈 Body Weight Over Time")
        st.line_chart(df.set_index("Date")[["Body Weight"]])

        st.subheader("💪 Muscle Mass & Fat Mass")
        st.line_chart(df.set_index("Date")[["Muscle Mass", "Fat Mass"]])

    except Exception as e:
        st.error(f"❌ Failed to load charts: {e}")

def show_workout_volume_chart():
    st.header("🏋️ Workout Volume Over Time")

    client = init_gsheet()
    try:
        workout_data = client.open(SHEET_NAME).worksheet(WORKOUT_SHEET).get_all_records()
        if not workout_data:
            st.info("No workout data to plot.")
            return

        df = pd.DataFrame(workout_data)
        df["Date"] = pd.to_datetime(df["Date"])
        df["Sets"] = pd.to_numeric(df["Sets"], errors="coerce")
        df["Reps"] = pd.to_numeric(df["Reps"], errors="coerce")
        df["Weight (kg)"] = pd.to_numeric(df["Weight (kg)"], errors="coerce")

        # Calculate total volume per row
        df["Total Volume"] = df["Sets"] * df["Reps"] * df["Weight (kg)"]

        # Group by date (sum of all exercises per day)
        volume_by_date = df.groupby("Date")["Total Volume"].sum().reset_index()

        # Plot line chart
        st.subheader("📆 Daily Total Training Volume")
        st.line_chart(volume_by_date.set_index("Date"))

    except Exception as e:
        st.error(f"❌ Failed to load volume chart: {e}")

# ---------- UI SECTIONS ----------
def workout_logger():
    st.header("📒 Log Workout")
    with st.form("workout_form"):
        w_date = st.date_input("Date", value=date.today())
        exercise = st.text_input("Exercise Name")
        sets = st.number_input("Sets", min_value=1, step=1)
        reps = st.number_input("Reps", min_value=1, step=1)
        weight = st.number_input("Weight (kg)", min_value=0.0, step=0.5)
        submitted = st.form_submit_button("Submit Workout")

        if submitted:
            log_workout(w_date, exercise, sets, reps, weight)
            st.success(f"✅ Workout logged: {exercise} ({sets}x{reps} @ {weight}kg)")

def metrics_tracker():
    st.header("📈 Track Body Metrics")
    with st.form("metrics_form"):
        m_date = st.date_input("Date", value=date.today(), key="metrics_date")
        body_weight = st.number_input("Body Weight (kg)", min_value=0.0, step=0.1)
        body_fat = st.number_input("Body Fat (%)", min_value=0.0, max_value=100.0, step=0.1)
        muscle_mass = st.number_input("Muscle Mass (kg)", min_value=0.0, step=0.1)
        fat_mass = st.number_input("Fat Mass (kg)", min_value=0.0, step=0.1)
        submitted = st.form_submit_button("Submit Body Metrics")

        if submitted:
            log_metrics(m_date, body_weight, body_fat, muscle_mass, fat_mass)
            st.success("✅ Body metrics logged successfully.")

# ---------- MAIN FUNCTION ----------
def main():
    st.set_page_config(page_title="FitSheet", layout="centered")
    st.title("🏋️‍♂️ FitSheet – Fitness Tracker")
    st.caption("Track your workouts and body metrics easily, synced to Google Sheets.")

    # Log workout
    workout_logger()

    # Log body metrics
    metrics_tracker()

    # Show history table
    show_data_preview()

    # Show progress charts
    show_progress_charts()

    # Show workout volume
    show_workout_volume_chart()

    st.markdown("---")
    st.caption("Made with 💪 using Python, Streamlit & Google Sheets")

# ---------- RUN ----------
if __name__ == "__main__":
    main()