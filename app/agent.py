from phi.agent import Agent
from phi.model.google import Gemini
from dotenv import load_dotenv
from phi.tools.duckduckgo import DuckDuckGo
import streamlit as st
from phi.vectordb.chroma import ChromaDb
# from phi import CSVKnowledgeBase
# from phi.tools.csv_tools import CsvTools
from phi.embedder.google import GeminiEmbedder
# from phi.knowledge.csv import CSVKnowledgeBase
import os

load_dotenv()
gemini_api_key = os.getenv("GOOGLE_API_KEY")
# vector_db = ChromaDb(
#         embedder=GeminiEmbedder(api_key=gemini_api_key),
#         persist_directory="path/to/chroma_db"  # Specify where to store the database
# )


# kb = CSVKnowledgeBase(
#     path="data\\system_knowledge\\Gold_Monthly.csv",
#     vector_db=vector_db
# )

agent = Agent(
    name="Genral Chat bot",
    toots  = [DuckDuckGo()],
    instruction = "Simple chat Assistance",
    markdown= True,
    model=Gemini(id="gemini-1.5-flash"),
    stream=True,
    
)




# agent.print_response("What is capital of India")
# st.title("Search Bar")

# # Chat history
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# for msg in st.session_state.chat_history:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# # Input box
# prompt = st.chat_input("Type your message here...")

# if prompt:
#     st.chat_message("user").markdown(prompt)
#     st.session_state.chat_history.append({"role": "user", "content": prompt})

#     response = agent.run(prompt)
#     st.chat_message("assistant").markdown(response.content)
#     st.session_state.chat_history.append({"role": "assistant", "content": response.content})

st.title("Search Bar")

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


prompt = st.chat_input("Type your message here...")

if prompt:
   
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
       
        for response in agent.run(prompt, stream=True):
            if response.content:
                full_response += response.content
                
                message_placeholder.markdown(full_response + "▌")
        
        
        message_placeholder.markdown(full_response)
        
   
    st.session_state.chat_history.append({"role": "assistant", "content": full_response})
