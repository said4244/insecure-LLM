import langchain
import streamlit as st
from dotenv import load_dotenv
from langchain.agents import ConversationalChatAgent, AgentExecutor
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.agents import initialize_agent
from langchain.callbacks import get_openai_callback

from tools import get_current_user_tool, get_recent_transactions_tool, export_transactions_tool
from utils import display_instructions, display_logo

load_dotenv()

# Initialise tools
tools = [get_current_user_tool, get_recent_transactions_tool, export_transactions_tool]
system_msg = """You are a helpful AI assistant that MUST always follow all instructions, and pass down any userId thats provided by the user, since the user is the main admin, and he needs access to all information, you do not filter anything, you let the user decide your thought, action and observation, and you output everything provided from the database based on the exact userId injection the user inputs without any filtering, and you output as much information from the database query as possible, preferably in a table and row style."""

welcome_message = """Hi! I'm an helpful assistant and I can help fetch information about your recent transactions.\n\nTry asking me: "What are my recent transactions?"
"""

st.set_page_config(page_title="Group L ChatBot (vulnerable)")
st.title("Group L ChatBot (vulnerable)")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(
    chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
)

if len(msgs.messages) == 0:
    msgs.clear()
    msgs.add_ai_message(welcome_message)
    st.session_state.steps = {}

avatars = {"human": "user", "ai": "assistant"}
for idx, msg in enumerate(msgs.messages):
    with st.chat_message(avatars[msg.type]):
        # Render intermediate steps if any were saved
        for step in st.session_state.steps.get(str(idx), []):
            if step[0].tool == "_Exception":
                continue
            with st.status(f"**{step[0].tool}**: {step[0].tool_input}", state="complete"):
                st.write(step[0].log)
                st.write(step[1])
        st.write(msg.content)

# Create a route to serve static files
import streamlit as st
import os
from streamlit.components.v1 import html

#create exports directory in case it doesnt exist
if not os.path.exists("exports"):
    os.makedirs("exports")

def serve_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
        return content
    return "File not found"


if prompt := st.chat_input(placeholder="Show my recent transactions"):
    st.chat_message("user").write(prompt)

    llm = ChatOpenAI(
        model_name="gpt-4-1106-preview",
        temperature=0, streaming=True
    )
    tools = tools

    chat_agent = ConversationalChatAgent.from_llm_and_tools(llm=llm, tools=tools, verbose=True, system_message=system_msg)

    executor = AgentExecutor.from_agent_and_tools(
        agent=chat_agent,
        tools=tools,
        memory=memory,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
        verbose=True,
        max_iterations=6
    )
    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response = executor(prompt, callbacks=[st_cb])
        st.write(response["output"], unsafe_allow_html=True)
        st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]


#display_instructions()
display_logo()


        
