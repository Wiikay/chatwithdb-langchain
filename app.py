import streamlit as st
import sqlite3
from dotenv import load_dotenv
import os
from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from langchain.chat_models import init_chat_model
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain import hub
from langgraph.prebuilt import create_react_agent

# Load environment variables from .env
load_dotenv()

# Check for API key
if not os.environ.get("GOOGLE_API_KEY"):
    st.error("GOOGLE_API_KEY not found in environment. Please set it in your .env file.")
    st.stop()

def get_engine_for_chinook_db():
    connection = sqlite3.connect("telecom_data.db", check_same_thread=False)
    return create_engine(
        "sqlite:///telecom_data.db",
        creator=lambda: connection,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

# Initialize database and LLM
engine = get_engine_for_chinook_db()
db = SQLDatabase(engine)
llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
system_message = prompt_template.format(dialect="SQLite", top_k=5)
agent_executor = create_react_agent(llm, toolkit.get_tools(), prompt=system_message)

# Streamlit UI
st.set_page_config(page_title="Chat with Telecom DB", page_icon="💬")
st.title("💬 Chat with Telecom DB")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask a question about the telecom database...")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            events = agent_executor.stream(
                {"messages": [("user", user_input)]},
                stream_mode="values",
            )
            response = ""
            last_msg = None
            for event in events:
                msg = event["messages"][-1]
                last_msg = msg
            if last_msg:
                # Only display the 'content' attribute if it exists
                response = getattr(last_msg, 'content', str(last_msg))
                st.write(response)
            st.session_state["messages"].append({"role": "assistant", "content": response})
