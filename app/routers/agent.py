import os
from dotenv import load_dotenv
import streamlit as st
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
from phi.knowledge.pdf import PDFKnowledgeBase, PDFReader
from phi.vectordb.chroma import ChromaDb
from phi.embedder.google import GeminiEmbedder
from phi.tools.newspaper4k import Newspaper4k
import uuid
from fastapi import HTTPException
from phi.knowledge.combined import CombinedKnowledgeBase


# Load env variables
load_dotenv()
gemini_api_key = os.getenv("GOOGLE_API_KEY")




UPLOAD_DIR = "data/uploads"
def load_combined_knowledge_base(file_path: str):
    import uuid
    import os

    # Create system and user vector DBs
    system_vector_db = ChromaDb(
        collection="ajit_doval_system",
        embedder=GeminiEmbedder(api_key=gemini_api_key)
    )
    unique_collection_name = f"uploaded_pdf_data_{uuid.uuid4()}"
    user_vector_db = ChromaDb(
        collection=unique_collection_name,
        embedder=GeminiEmbedder(api_key=gemini_api_key)
    )

    # Create knowledge bases
    system_kb = PDFKnowledgeBase(
        path=os.path.join("data", "system_knowledge", "Ajit_Doval_Biography.pdf"),
        vector_db=system_vector_db,
        reader=PDFReader(chunk_size=100, chunk_overlap=10, ignore_images=True, skip_empty=True)
    )

    user_kb = PDFKnowledgeBase(
        path=file_path,
        vector_db=user_vector_db,
        reader=PDFReader(chunk_size=100, chunk_overlap=10, ignore_images=True, skip_empty=True)
    )

    # Load system and user knowledge base — do this only once
    try:
        print("Loading system knowledge base...")
        system_kb.load(upsert=False)
    except Exception as e:
        print(f"Failed to load system KB: {e}")

    try:
        print("Loading user knowledge base...")
        user_kb.load(upsert=True)
    except Exception as e:
        print(f"Failed to load user KB: {e}")

    # Create a new combined vector DB
    combined_vector_db = ChromaDb(
        collection=f"combined_kb_{uuid.uuid4()}",
        embedder=GeminiEmbedder(api_key=gemini_api_key)
    )

    # Combine without calling load again
    combined_kb = CombinedKnowledgeBase(
        sources=[system_kb, user_kb],
        vector_db=combined_vector_db
    )

    try:
        print("Loading user knowledge base...")
        combined_kb.load(upsert=True)
    except Exception as e:
        print(f"Failed to load user KB: {e}")
    return combined_kb

def create_agent(knowledge: CombinedKnowledgeBase):
    print("Combined KB sources:",knowledge)
    # for source in knowledge.sources:
    #   print("-", source)
    agent= Agent(
        name="PDF Assistant",
        tools=[DuckDuckGo(), Newspaper4k()],
        description="An AI assistant to answer questions from your uploaded PDF or basic query.",
        instructions=[
            """
            System Knowledge Base (Ajit Doval):
                - Use system knowledge base as primary source for Ajit Doval related queries
                - Share all available information from the knowledge base
                - Include both public and classified information if available
            
            Information Retrieval Priority:
            1. Knowledge Base Search:
                - Search both system and user-uploaded PDFs
                - Share all information (both private and public )
                - Provide complete and accurate details
            
            2. Web Search (if knowledge base lacks information):
                - Search top 5 relevant links via DuckDuckGo
                - Extract and analyze content using Newspaper4k
                - Skip unavailable URLs
                - Filter out:
                    * Video links
                    * Promotional content
                    * Redundant information
            
            Response Guidelines:
            1. Structure:
                - Use step-by-step format
                - Include clear headings
                - Add bullet points or numbered lists
                - Use code blocks for technical content
            
            2. Writing Style:
                - Be clear and concise
                - Focus on actionable information
                - Maintain friendly, conversational tone
                - Avoid filler words ("here", "etc.", "kind of")
            
            3. Context Awareness:
                - Build on previous conversation
                - Avoid repeating information
                - Use knowledge base only when relevant
            
            4. Interaction Protocol:
                - Greet: "Hey!", "Hi there!"
                - Thanks: "Sure!", "You're welcome!"
                - Farewell: "Take care!", "Catch you later!"
                - Handle negative messages with calm professionalism
            """
        ],
        model=Gemini(id="gemini-1.5-flash"),
        markdown=True,
        knowledge_base =knowledge,
        add_references=True,
        # debug_mode=True
    )
    # agent.print_response("when ajit is appointed as National Security Advisor ")
    # agent.print_response("How can we make Beef&in&Beer? ")
    return agent


