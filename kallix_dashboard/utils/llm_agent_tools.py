import streamlit as st

def agent_selector():
    agents = ["Ananya (Real Estate)", "Aisha (Chiropractor)", "Mira (E-commerce)"]
    agent = st.selectbox("Select an Agent", agents)
    st.success(f"Selected Agent: {agent}")
    return agent

def knowledge_base_tool(agent):
    st.write(f"Manage Knowledge Base for **{agent}**")
    link = st.text_input("🔗 Add Knowledge Base Link")
    file = st.file_uploader("📄 Upload Knowledge Base Document", type=["txt", "doc", "docx"])
    if st.button("Save Knowledge Base"):
        st.success("Knowledge Base linked successfully.")
