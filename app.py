# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (Final Sürüm - Final Syntax Fix 4)
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

# Other imports
try:
    from chromadb import Client, Settings
    from chromadb.api.models.Collection import Collection
except ImportError as e: st.error(f"Kritik Import Hatası: chromadb yüklenemedi. {repr(e)}"); st.stop()
try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
except ImportError as e: st.error(f"Kritik Import Hatası: langchain_google_genai yüklenemedi. {repr(e)}"); st.stop()
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError as e: st.error(f"Kritik Import Hatası: langchain_text_splitters yüklenemedi. {repr(e)}"); st.stop()
try:
    from langchain_community.document_loaders import PyPDFLoader
except ImportError as e: st.error(f"Kritik Import Hatası: langchain_community.document_loaders yüklenemedi. {repr(e)}"); st.stop()


# --- 1. API Key ---
try:
    print("--- DEBUG: Reading Secrets... ---")
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    print("--- DEBUG: Secrets Read OK. ---")
# ===========================================
# SYNTAX ERROR FIX HERE
except KeyError:
    print("!!! GEMINI_API_KEY not found in Secrets! ---")
    st.error("HATA: Streamlit Secrets'ta 'GEMINI_API_KEY' bulunamadı.") # Corrected string
    st.stop()
# ===========================================
except Exception as e:
    print(f"!!! Unexpected error reading Secrets: {e} !!!")
    st.error(f"Secrets okunurken HATA: {repr(e)}") # Use repr(
