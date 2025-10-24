import streamlit as st
import requests

# Flask API endpoint
API_URL = "http://localhost:5000/answer"  # Change if deployed elsewhere

st.set_page_config(page_title="RAG Chatbot", layout="wide")

# Sidebar for question history
st.sidebar.title(" Question History")
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous user questions in sidebar
user_questions = [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"]
if user_questions:
    for i, q in enumerate(user_questions, 1):
        st.sidebar.markdown(f"{i}. {q}")
else:
    st.sidebar.write("No questions yet.")

# Clear history button
if st.sidebar.button("Clear History"):
    st.session_state.messages = []
    st.experimental_rerun()

# Main UI
st.title("HR Policy Chatbot")
st.write("Ask me anything about HR policies!")

# Display previous messages in chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# User input
if prompt := st.chat_input("Type your question here..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call Flask API
    try:
        with st.spinner("Fetching answer..."):
            response = requests.post(API_URL, json={"query": prompt})

        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "No answer found.")
            sources = data.get("sources", [])

            # Display answer
            with st.chat_message("assistant"):
                st.markdown(f"**Answer:** {answer}")

                # Collapsible section for sources
                if sources:
                    with st.expander("View Sources"):
                        for src in sources:
                            if "Score:" in src:
                                score_str = src.split("Score:")[-1].strip(")")
                                score = float(score_str)
                                if score >= 0.85:
                                    badge = " High"
                                    color = "green"
                                elif score >= 0.7:
                                    badge = " Medium"
                                    color = "orange"
                                else:
                                    badge = " Low"
                                    color = "red"
                                st.markdown(f"- {src} | **Confidence:** <span style='color:{color}'>{badge}</span>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"- {src}")

            # Save bot reply in history (only answer)
            st.session_state.messages.append({"role": "assistant", "content": f"**Answer:** {answer}"})

        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Failed to connect to API: {e}")