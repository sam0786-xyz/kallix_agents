import streamlit as st

def phone_tool(agent):
    st.write(f"📞 Phone Interaction for {agent}")
    exotel_link = st.text_input("Enter Exotel Call Link or Flow URL")
    if st.button("Trigger Call"):
        if exotel_link:
            st.success(f"📞 Call initiated via Exotel: {exotel_link}")
        else:
            st.warning("Please provide a valid call link.")
