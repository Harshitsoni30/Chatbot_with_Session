# @app.post("/session/chat")
# async def create_chat_session(
#     chat_data: ChatSessionInput,
#     current_user: dict = Depends(get_current_user)
# ):
#     session_id = chat_data.session_id
#     prompt = chat_data.prompt

#     # Initialize agent
#     agent = Agent(
#         name="General Chatbot",
#         tools=[DuckDuckGo()],
#         instruction="You are a helpful assistant. Always remember previous user questions and facts. Use them to answer follow-up questions.",
#         markdown=True,
#         model=Gemini(id="gemini-1.5-flash"),
#         stream=True
#     )

#     # 1. Load previous chat history (if any)
#     existing_session = await session_title_collection.find_one({
#         "session_id": session_id,
#         "user_email": current_user["email"]
#     })

#     chat_history_prompt = ""
#     if existing_session and "message" in existing_session:
#         for msg in existing_session["message"]:
#             role = msg["role"]
#             content = msg["content"]
#             chat_history_prompt += f"{role.capitalize()}: {content}\n"
    
#     # 2. Append new user prompt
#     full_prompt = chat_history_prompt + f"User: {prompt}\nAssistant:"
#     full_response = ""
#     for response in agent.run(full_prompt, stream=True):
#         if response.content:
#             full_response += response.content

#     # Prepare message format
#     user_msg = {"role": "user", "content": prompt}
#     assistant_msg = {"role": "assistant", "content": full_response}

#     # 4. Save to DB
#     if existing_session:
#         await session_title_collection.update_one(
#             {"session_id": session_id, "user_email": current_user["email"]},
#             {
#                 "$push": {
#                     "message": {"$each": [user_msg, assistant_msg]}
#                 },
#                 "$set": {"updated_at": datetime.utcnow()}
#             }
#         )
#     else:
#         title = generate_title(prompt)
#         new_session = {
#             "session_id": session_id,
#             "user_email": current_user["email"],
#             "title": title,
#             "message": [user_msg, assistant_msg],
#             "created_at": datetime.utcnow()
#         }
#         await session_title_collection.insert_one(new_session)

#     return {
#         "session_id": session_id,
#         "reply": full_response
#     }


# @app.post("/session/chat")
# async def create_chat_session_stream(
#     chat_data: ChatSessionInput,
#     # current_user: dict = Depends(get_current_user)
# ):
#     session_id = chat_data.session_id
#     prompt = chat_data.prompt

#     agent = Agent(
#         name="General Chatbot",
#         tools=[DuckDuckGo()],
#         instruction="You are a helpful assistant. Always remember previous user questions and facts. Use them to answer follow-up questions.",
#         markdown=True,
#         model=Gemini(id="gemini-1.5-flash"),
#         stream=True
#     )

   
#     existing_session = await session_title_collection.find_one({
#         "session_id": session_id,
#         # "user_email": current_user["email"]
#     })

#     chat_history_prompt = ""
#     if existing_session and "message" in existing_session:
#         for msg in existing_session["message"]:
#             chat_history_prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"

#     full_prompt = chat_history_prompt + f"User: {prompt}\nAssistant:"
#     full_response = ""

#     async def stream_response():
#         nonlocal full_response
#         response = agent.run(full_prompt, stream=True)
#         # print(response)
#         for chunk in response:
#             if chunk and chunk.content:
#                 full_response += chunk.content
#                 yield chunk.content
#                 # await asyncio.sleep(0.5)  
       
        
#         user_msg = {"role": "user", "content": prompt}
#         assistant_msg = {"role": "assistant", "content": full_response}

#         if existing_session:
#             await session_title_collection.update_one(
#                 {"session_id": session_id,
#                 #   "user_email": current_user["email"]
#                   },
#                 {
#                     "$push": {
#                         "message": {"$each": [user_msg, assistant_msg]}
#                     },
#                     "$set": {"updated_at": datetime.utcnow()}
#                 }
#             )
#         else:
#             title = generate_title(prompt)
#             new_session = {
#                 "session_id": session_id,
#                 # "user_email": current_user["email"],
#                 "title": title,
#                 "message": [user_msg, assistant_msg],
#                 "created_at": datetime.utcnow()
#             }
#             await session_title_collection.insert_one(new_session)

#     # return StreamingResponse()
#     return StreamingResponse(
#             stream_response(),
#             media_type="text/plain",
#             headers={
#                 "Cache-Control": "no-cache",
#                 "Connection": "keep-alive",
#                 "Content-Type": "text/event-stream",
#             },
#         )

###for knowledge base
def load_knowledge_base(file_path: str):
#     unique_collection_name = f"uploaded_pdf_data_{uuid.uuid4()}"
#     vector_db = ChromaDb(
#         collection=unique_collection_name,
#         embedder=GeminiEmbedder(api_key=gemini_api_key)
#     )
#     knowledge = PDFKnowledgeBase(
#         path=file_path,
#         vector_db=vector_db,
#         reader=PDFReader(
#             chunk_size=100,  # Reduce from default to1300
#             chunk_overlap=10,  # Add small overlap to mai1tain context
#             ignore_images=True,
#             skip_empty=True
#         )    )
#     if not vector_db.exists():
#         knowledge.load(upsert=True)
#     return knowledge
    
# def system_knowledge_base():
#     vector_db = ChromaDb(
#         collection="system_data",
#         embedder=GeminiEmbedder(api_key=gemini_api_key)
#     ) 
    
    
    
#     knowledge_base = PDFKnowledgeBase(
#         path = "app/data/system_knowledge/Ajit_Doval_Biography.pdf",
#         vector_db=vector_db,
#         reader=PDFReader(
#             chunk_size=100,  # Reduce from default to1300
#             chunk_overlap=10,  # Add small overlap to mai1tain context
#             ignore_images=True,
#             skip_empty=True
#         )    )
    
#     knowledge_base.load(upsert=True)

#     return knowledge_base

# def load_combined_knowledge_base(file_path :str):
#     user_kb = load_knowledge_base(file_path)
#     system_kb = system_knowledge_base()

#     combined_vector_db = ChromaDb(
#     collection="combined_documents",
#     embedder=GeminiEmbedder(api_key=gemini_api_key)
# )

#     combined_kb = CombinedKnowledgeBase(
#         sources=[user_kb, system_kb],
#         vector_db=combined_vector_db 

#     )
   
#     combined_kb.load(upsert=True)
#     return combined_kb
# def load_combined_knowledge_base(file_path: str):
#     user_kb = load_knowledge_base(file_path)
#     system_kb = system_knowledge_base()

#     # Create a new unique collection name for combined KB
#     combined_collection_name = f"combined_kb_{uuid.uuid4()}"
    
#     combined_vector_db = ChromaDb(
#         collection=combined_collection_name,
#         embedder=GeminiEmbedder(api_key=gemini_api_key)
#     )

#     combined_kb = CombinedKnowledgeBase(
#         sources=[system_kb, user_kb],  
#         vector_db=combined_vector_db
#     )
    
#     # Force upsert=the combined knowledge base
#     combined_kb.load(upsert=True)
#     return combined_kb



# def load_combined_knowledge_base(file_path:str):
#     # Create separate collections for user and system knowledge
#     system_vector_db = ChromaDb(
#         collection="thai_recipies",
#         embedder=GeminiEmbedder(api_key=gemini_api_key)
#     )
    
#     user_vector_db = ChromaDb(
#         collection="ajit_doval_system",
#         embedder=GeminiEmbedder(api_key=gemini_api_key)
#     )
    
#     # Create knowledge bases
#     system_kb = PDFKnowledgeBase(
#         path="data/system_knowledge/ThaiRecipes.pdf",
#         vector_db=system_vector_db,
#         reader=PDFReader(
#             chunk_size=100,
#             chunk_overlap=10,
#             ignore_images=True,
#             skip_empty=True
#         )
#     )
    
#     user_kb = PDFKnowledgeBase(
#         path="data\\system_knowledge\\Ajit_Doval_Biography.pdf",
#         vector_db=user_vector_db,
#         reader=PDFReader(
#             chunk_size=100,
#             chunk_overlap=10,
#             ignore_images=True,
#             skip_empty=True
#         )
#     )
    
#     # Force load both knowledge bases
#     system_kb.load(upsert=True)
#     if user_vector_db.exists():
#         user_kb.load(upsert=True)
#     else:
#         print("User vector DB collection not found")
    
#     # Create combined knowledge base
#     combined_vector_db = ChromaDb(
#         collection=f"combined_kb_{uuid.uuid4()}",
#         embedder=GeminiEmbedder(api_key=gemini_api_key)
#     )
    
#     combined_kb = CombinedKnowledgeBase(
#         sources=[system_kb, user_kb],
#         vector_db=combined_vector_db
#     )
    
#     # Load combined knowledge base
#     combined_kb.load(upsert=True)
#     return combined_kb


# from langchain.embeddings import GooglePalmEmbeddings
# from langchain.retrievers import EnsembleRetriever
# from langchain.vectorstores.pgvector import PGVector
# from phi.knowledge.langchain import LangChainKnowledgeBase
# from phi.agent import Agent, RunResponse
# from phi.embedder.google import GeminiEmbedder
# from langchain.vectorstores.mongodb_atlas import MongoDBAtlasVectorSearch
# from db.session import session_collection, session_title_collection

# embedding_model = GeminiEmbedder(api_key=gemini_api_key)  # Use Gemini for embeddings

# # Define your PostgreSQL connection string here

# # MongoDB Atlas connection string and collection details




# embedding_model = GeminiEmbedder(api_key=gemini_api_key)  # Use Gemini for embeddings

# static_vectorstore = ChromaDb(
#     collection_name="cocktail-codex",
#     embedding_function=embedding_model,
#     collection_name=session_collection,
# )
# dynamic_vectorstore =ChromaDb(
#     collection_name="evernotes",
#     embedding_function=embedding_model,
#     connection_string=session_collection,

# )


# static_retriever = static_vectorstore.as_retriever()
# dynamic_retriever = dynamic_vectorstore.as_retriever()


# ensemble_retriever = EnsembleRetriever(
#     retrievers=[dynamic_retriever, static_retriever],
    
# # )
# from langchain.vectorstores import Chroma
# from langchain.retrievers import EnsembleRetriever
# from langchain_google_genai import GoogleGenerativeAIEmbeddings

# from phi.knowledge.langchain import LangChainKnowledgeBase
# from phi.agent import Agent, RunResponse
# from langchain.document_loaders import PyPDFLoader
# from langchain.embeddings import HuggingFaceEmbeddings

# # Initialize Gemini embedding model
# embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


# # Define ChromaDB persistent storage paths
# static_chroma_path = "chroma_db/static"
# dynamic_chroma_path = "chroma_db/dynamic"

# # Initialize Chroma vector stores
# static_vectorstore = Chroma(
#     collection_name="cocktail-codex",
#     embedding_function=embedding_model,
#     persist_directory=static_chroma_path
# )

# dynamic_vectorstore = Chroma(
#     collection_name="evernotes",
#     embedding_function=embedding_model,
#     persist_directory=dynamic_chroma_path
# )

# Create retrievers
# static_retriever = static_vectorstore.as_retriever()
# dynamic_retriever = dynamic_vectorstore.as_retriever()

# Ensemble Retriever
# ensemble_retriever = EnsembleRetriever(
#     retrievers=[dynamic_retriever, static_retriever],
#     weights=[0.5, 0.5]
# )
# def load_knowledge_base(pdf_path: str):
#     loader = PyPDFLoader(pdf_path)
#     documents = loader.load()
#     try:
#         vectorstore = Chroma.from_documents(
#             documents,
#             embedding=embedding_model,
#             persist_directory="chroma_db/dynamic",
#             collection_name="user-uploaded"
#         )
#     except Exception as e:
#         print(f"Embedding failed: {e}1)
#         raise HTTPException(status_code=300, detail="Embedding failed. Please try again later.")
  
#     retriever = vectorstore.as_retriever()
#     return LangChainKnowledgeBase(retriever=retriever)
