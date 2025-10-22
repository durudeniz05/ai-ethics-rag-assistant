# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (Minimal Debug - Embedding Test)
# =================================================================================

import streamlit as st
import os
import glob
import tempfile
import textwrap
import traceback # Import traceback at the top

# RAG Bileşenleri - Import Block
# ===========================================
try:
    import google.generativeai
    print("--- google.generativeai successfully imported ---")
    genai = google.generativeai

    APIError_class = None
    if hasattr(genai, 'errors') and hasattr(genai.errors, 'APIError'):
        APIError_class = genai.errors.APIError
        print(f"--- APIError found under genai.errors: {APIError_class} ---")
    elif hasattr(genai, 'APIError'):
         APIError_class = genai.APIError
         print(f"--- APIError found directly under genai: {APIError_class} ---")

    if APIError_class is None:
        print("!!! APIError class NOT found under genai or genai.errors !!!")
        APIError = Exception
    else:
        APIError = APIError_class
        print(f"--- APIError assigned successfully: {APIError} ---")

except ImportError as e:
    print(f"!!! FAILED to import google.generativeai:")
    print(repr(e))
    st.error(f"Critical Import Error: Failed to load google.generativeai. Details: {repr(e)}")
    st.stop()
except AttributeError as e:
    print(f"!!! AttributeError while searching for APIError (genai.errors might be missing): {e} !!!")
    APIError = Exception
    print("--- Using general Exception for APIError ---")
except Exception as e:
    print(f"!!! Unexpected error during import block:")
    print(repr(e))
    st.error(f"Critical Startup Error during imports. Details: {repr(e)}")
    st.stop()
# ===========================================

# Other imports
try: from chromadb import Client, Settings; print("--- chromadb imported successfully ---")
except ImportError as e: print(f"!!! FAILED to import chromadb:"); print(repr(e)); st.error(f"Critical Import Error: Failed to load chromadb. Details: {repr(e)}"); st.stop()
try: from langchain_google_genai import GoogleGenerativeAIEmbeddings; print("--- langchain_google_genai imported successfully ---")
except ImportError as e: print(f"!!! FAILED to import langchain_google_genai:"); print(repr(e)); st.error(f"Critical Import Error: Failed to load langchain_google_genai. Details: {repr(e)}"); st.stop()
try: from langchain_text_splitters import RecursiveCharacterTextSplitter; print("--- langchain_text_splitters imported successfully ---")
except ImportError as e: print(f"!!! FAILED to import langchain_text_splitters:"); print(repr(e)); st.error(f"Critical Import Error: Failed to load langchain_text_splitters. Details: {repr(e)}"); st.stop()
try: from langchain_community.document_loaders import PyPDFLoader; print("--- langchain_community.document_loaders imported successfully ---")
except ImportError as e: print(f"!!! FAILED to import langchain_community.document_loaders:"); print(repr(e)); st.error(f"Critical Import Error: Failed to load langchain_community.document_loaders. Details: {repr(e)}"); st.stop()


# --- 1. API Key ---
try:
    print("--- DEBUG: Reading Secrets... ---")
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    print("--- DEBUG: Secrets Read OK. ---")
except KeyError: print("!!! GEMINI_API_KEY not found in Secrets! ---"); st.error("Error: 'GEMINI_API_KEY' not found in Streamlit Secrets."); st.stop()
except Exception as e: print(f"!!! Unexpected error reading Secrets: {e} !!!"); st.error(f"Error reading Secrets: {e}"); st.stop()

# --- 2. Setup Components (Embedding Test) ---
# Cache disabled
def setup_rag_components():
    """(DEBUG) Configure, Splitter ve Embedding test ediliyor."""
    print("--- DEBUG: setup_rag_components START ---")
    llm, embedding_function, text_splitter, collection = None, None, None, None
    try:
        print("--- DEBUG: Calling genai.configure... ---")
        genai.configure(api_key=GEMINI_API_KEY)
        print("--- DEBUG: genai.configure OK. ---")

        # ===========================================
        # --- Embedding ENABLED ---
        embedding_model_name = "models/text-embedding-004"
        print(f"--- DEBUG: Creating GoogleGenerativeAIEmbeddings ({embedding_model_name})... ---")
        embedding_function = GoogleGenerativeAIEmbeddings( # UNCOMMENTED
            model=embedding_model_name,
            google_api_key=GEMINI_API_KEY
        )
        print(f"--- DEBUG: GoogleGenerativeAIEmbeddings created: {embedding_function} ---")
        # embedding_function = "DEBUG: Embedding Disabled" # REMOVED
        # ===========================================

        # --- SPLITTER ENABLED ---
        print("--- DEBUG: Creating RecursiveCharacterTextSplitter... ---")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        print(f"--- DEBUG: RecursiveCharacterTextSplitter created: {text_splitter} ---")
        # --- End Enabled ---

        # --- ChromaDB DISABLED ---
        collection = None
        print("--- DEBUG: ChromaDB intentionally None ---")
        # --- End Disabled ---

        # --- LLM DISABLED ---
        llm = "DEBUG: LLM Disabled"
        print("--- DEBUG: LLM intentionally disabled ---")
        # --- End Disabled ---

    except Exception as e:
        print(f"!!! Error during setup_rag_components:")
        print(repr(e))
        st.error(f"CRITICAL ERROR during component setup (Embedding/Splitter?). Details: {repr(e)}")
        st.stop() # Stop if any setup step fails

    print("--- DEBUG: setup_rag_components END (embedding active) ---")
    return llm, embedding_function, text_splitter, collection # Return actual embedding/splitter

# --- Dummy Functions ---
def index_documents(uploaded_files, collection, text_splitter, embedding_function): return 0,0
def ask_rag_assistant(question, llm, collection, embedding_function): return "DEBUG MODE"

# --- 3. Main App Logic ---
def main():
    print("--- DEBUG: main() START ---")
    st.set_page_config(page_title="Embedding Test")
    st.title("Setup Function Test: Embedding") # Title updated
    st.write("If you see this, Secrets read, configure called, Splitter & Embedding init attempted.")

    llm, embedding_function, text_splitter, collection = None, None, None, None
    try:
        print("--- DEBUG: Calling setup_rag_components (embedding test)... ---")
        llm, embedding_function, text_splitter, collection = setup_rag_components()
        print(f"--- DEBUG: Returned from setup_rag_components. Embedding type: {type(embedding_function)} ---")
    except Exception as e:
        print(f"!!! ERROR calling setup_rag_components from main: {e} !!!")
        st.error(f"Application failed to initialize during setup call: {e}")
        st.stop()

    # --- Debug Check (Check if Embedding & Splitter are objects, others are string/None) ---
    st.success("DEBUG: Reached point after setup_rag_components call.")
    st.info(f"LLM Status: {llm} (Type: {type(llm)})")
    st.info(f"Embedding Status: {embedding_function} (Type: {type(embedding_function)})")
    st.info(f"Splitter Status: {text_splitter} (Type: {type(text_splitter)})")
    st.info(f"Collection Status: {collection} (Type: {type(collection)})")

    if not isinstance(embedding_function, GoogleGenerativeAIEmbeddings) or not isinstance(text_splitter, RecursiveCharacterTextSplitter):
        st.error("Embedding or Splitter did not initialize correctly!")
    else:
        st.success("Embedding and Splitter seem OK. The issue might be later or intermittent.")

    st.info("Test finished. Next step depends on whether this screen loaded.")

if __name__ == "__main__":
    main()
