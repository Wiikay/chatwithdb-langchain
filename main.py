import sqlite3

import requests
from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
import getpass
import os
from langchain.chat_models import init_chat_model
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit


def get_engine_for_chinook_db():
    connection = sqlite3.connect("telecom_data.db", check_same_thread=False)
    return create_engine(
        "sqlite:///telecom_data.db",  # Fixed: use three slashes for relative path
        creator=lambda: connection,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )


engine = get_engine_for_chinook_db()

db = SQLDatabase(engine)


if not os.environ.get("GOOGLE_API_KEY"):
  os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")



toolkit = SQLDatabaseToolkit(db=db, llm=llm)
print(toolkit,"Toolkit")


toolkit.get_tools()

from langchain import hub

prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")

assert len(prompt_template.messages) == 1
print(prompt_template.input_variables)


system_message = prompt_template.format(dialect="SQLite", top_k=5)

from langgraph.prebuilt import create_react_agent

agent_executor = create_react_agent(llm, toolkit.get_tools(), prompt=system_message)

example_query = "give me top 5 customers based on call duration?"

events = agent_executor.stream(
    {"messages": [("user", example_query)]},
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()