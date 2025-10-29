import streamlit as st

def email_tool(agent):
    st.write(f"📤 Send Email as {agent}")
    email_to = st.text_input("Recipient Email")
    subject = st.text_input("Subject")
    body = st.text_area("Email Body")
    if st.button("Send Email"):
        if email_to and subject and body:
            st.success(f"Email sent successfully to {email_to}!")
        else:
            st.warning("Please fill all fields before sending.")
