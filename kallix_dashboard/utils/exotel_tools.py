import streamlit as st

def phone_tool(agent, account_sid, trial_number, flow_id):
    st.write(f"📞 Connect or Trigger Calls for **{agent}**")
    st.markdown("Use your registered Exotel number to handle AI-powered calls.")
    
    st.markdown(f"""
    **Exotel Account SID:** `{account_sid}`  
    **Trial Number:** `{trial_number}`  
    **Flow ID:** `{flow_id}`
    """)

    phone_number = st.text_input("Enter client phone number to call")
    if st.button("Trigger Exotel Call"):
        if phone_number:
            st.success(f"📞 AI Agent ({agent}) will call {phone_number} via Exotel Flow {flow_id}.")
            st.info("Note: Once Exotel setup is active, this button will trigger real calls.")
        else:
            st.warning("Please enter a phone number first.")
