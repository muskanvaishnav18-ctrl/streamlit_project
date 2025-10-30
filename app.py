import streamlit as st
import requests

# Flask API endpoint
API_URL = "http://localhost:5000/answer"

st.set_page_config(page_title="Leave  Policy Chatbot", layout="wide")

# Sidebar for question history
st.sidebar.title("Question History")
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
    st.rerun()  # Updated from experimental_rerun

# Main UI
st.title("Leave Policy Chatbot")
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
            # Added timeout and better error handling
            response = requests.post(
                API_URL, 
                json={"query": prompt},
                timeout=30,
                headers={"Content-Type": "application/json"}
            )

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
                            st.markdown(f"- **{src}**")

            # Save bot reply in history
            st.session_state.messages.append({"role": "assistant", "content": f"**Answer:** {answer}"})

        else:
            error_msg = f"API Error: {response.status_code}"
            st.error(error_msg)
            st.error(f"Response: {response.text[:500]}")  # Show first 500 chars
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to Flask API. Make sure Flask is running on http://localhost:5000")
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. The server is taking too long to respond.")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
