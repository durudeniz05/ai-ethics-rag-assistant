# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (Final Sürüm - Doğru APIError Import)
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
    # ===========================================
    # APIError İÇİN DOĞRU IMPORT KULLANILDI
    from google.generativeai import APIError
    # ===========================================
    print("--- google.generativeai and APIError imported successfully ---") # Log temizliği için bu print kalabilir
except ImportError as e:
    st.error(f"Kritik Import Hatası: google.generativeai yüklenemedi. {repr(e)}")
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
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("HATA: Streamlit Secrets'ta 'GEMINI_API_KEY' bulunamadı.")
    st.stop()
except Exception as e:
    st.error(f"Secrets okunurken HATA: {e}")
    st.stop()

# --- 2. Setup Components (Cache Enabled) ---
@st.cache_resource # Cache etkin
def setup_rag_components():
    """Tüm RAG bileşenlerini başlatır ve cache'ler."""
    print("--- DEBUG: setup_rag_components ÇALIŞTIRILIYOR (cache ile)... ---") # Sadece ilk çalıştırmada veya cache yenilenince görünmeli
    try:
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)

        # Embedding Model
        embedding_model_name = "models/text-embedding-004"
        embedding_function = GoogleGenerativeAIEmbeddings(
            model=embedding_model_name,
            google_api_key=GEMINI_API_KEY
        )

        # Text Splitter
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

        # ChromaDB (In-Memory)
        import chromadb
        chroma_client = chromadb.Client()
        collection_name = "ai_ethics_manual_collection"
        try: chroma_client.delete_collection(name=collection_name) # Her başlangıçta temizle
        except: pass
        collection = chroma_client.get_or_create_collection(name
