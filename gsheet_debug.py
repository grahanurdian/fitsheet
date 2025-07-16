import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread

st.title("🧪 GSheet Connectivity Test")

try:
    st.write("🔐 Attempting to read Google Sheets credentials...")

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        dict(st.secrets["gcp"]),
        scope
    )

    st.write("✅ Credentials loaded")

    client = gspread.authorize(creds)
    st.write("📄 Gspread authorized")

    # Try listing spreadsheets (will succeed only if access is granted)
    sheets = client.openall()
    sheet_titles = [s.title for s in sheets]

    st.success(f"✅ Connected! Found {len(sheet_titles)} sheets:")
    st.write(sheet_titles)

except Exception as e:
    st.error(f"❌ Failed: {e}")