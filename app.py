# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (Minimal Debug - Final Import Syntax Fix)
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

# Other imports (Corrected try-except structure)
# ===========================================
try:
    from chromadb import Client, Settings
    print("--- chromadb imported successfully ---")
except ImportError as e:
    print(f"!!! FAILED to import chromadb:")
    print(repr(e))
    st.error(f"Critical Import Error: Failed to load chromadb. Details: {repr(e)}")
    st.stop()

try: # <-- Start try for langchain_google_genai
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    print("--- langchain_google_genai imported successfully ---")
# <-- End try, except must follow immediately and be aligned
except ImportError as e:
    print(f"!!! FAILED to import langchain_google_genai:")
    print(repr(e))
    st.error(f"Critical Import Error: Failed to load langchain_google_genai. Details: {repr(e)}")
    st.stop()

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    print("--- langchain_text_splitters imported successfully ---
