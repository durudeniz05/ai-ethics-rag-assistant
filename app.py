# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (Final Sürüm - Final Structure Check 2)
# =================================================================================

import streamlit as st
import os
import glob
import tempfile
import textwrap
import traceback # Hata takibi için

# RAG Bileşenleri - Import Block
# ===========================================
try:
    import google.generativeai as genai
    from google.generativeai.errors import APIError # Corrected APIError import path
    # print("--- google.generativeai and APIError imported successfully ---")
except ImportError as e:
    st.error(f"Kritik Import Hatası: google.generativeai veya APIError yüklenemedi. {repr(e)}")
    st.stop()
except Exception as e:
    st.error(f"Kritik Başlangıç Hatası (google import): {repr(e)}")
    st.stop()
# ===========================================

# Other imports (Corrected try-except structure)
# ===========================================
try: # Try block for chromadb
    from chromadb import Client, Settings
    from chromadb.api.models.Collection import Collection
    # print("--- chromadb imported successfully ---")
except ImportError as e: # Except block aligned with try
    print(f"!!! FAILED to import chromadb:")
    print(repr(e))
    st.error(f"Critical Import Error: Failed to load chromadb. Details: {repr(e)}")
    st.stop()

try: # Try block for langchain_google_genai
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    # print("--- langchain_google_genai imported successfully ---")
except ImportError as e: # Except block aligned with try
    print(f"!!! FAILED to import langchain_google_genai:")
    print(repr(e))
    st.error(f"Critical Import Error: Failed to load langchain_google_genai. Details: {repr(e)}")
    st.stop()

try: # Try block for langchain_text_splitters
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    # print("--- langchain_text_splitters imported successfully ---")
except ImportError as e: # Except block aligned with try
    print(f"!!! FAILED to import langchain_text_splitters:")
    print(repr(e))
    st.error(f"Critical Import Error: Failed to load langchain_text_splitters. Details: {repr(e)}")
    st.stop()

try: # Try block for langchain_community
    from langchain_community.document_loaders import PyPDFLoader
    # print("--- langchain_community.document_loaders imported successfully ---")
except ImportError as e: # Except block aligned with try
    print(f"!!! FAILED to import langchain_community.document_loaders:")
    print(repr(e))
    st.error(f"Critical Import Error: Failed to load langchain_community.document_loaders. Details: {repr(e)}")
    st.stop()
# ===========================================


# --- 1. API Key ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError: st.error("HATA: Streamlit Secrets'ta 'GEMINI_API_KEY' bulunamadı."); st.stop()
except Exception as e: st.error(
