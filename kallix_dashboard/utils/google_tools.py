import streamlit as st

def google_sheet_tool():
    st.write("🔗 Connect to Google Sheet")
    sheet_code = st.text_input("Enter Google Sheet Code")
    if st.button("Connect"):
        if sheet_code:
            st.success(f"Connected to Google Sheet: {sheet_code}")
        else:
            st.error("Please enter a valid sheet code.")
