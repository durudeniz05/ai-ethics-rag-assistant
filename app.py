# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (Final Sürüm - Cache Etkin)
# =================================================================================

import streamlit as st
import os
import glob
import tempfile
import textwrap
import traceback # Hata takibi için

# RAG Bileşenleri - Import Block
# ===========================================
# APIError için doğru import yolunu belirlemiştik (genai.errors)
try:
    import google.generativeai as genai
    from google.generativeai.errors import APIError
    print("--- google.generativeai and APIError imported successfully ---")
except ImportError as e:
    # Bu hata olmamalı ama olursa gösterelim
    st.error(f"Kritik Import Hatası: google.generativeai yüklenemedi. {repr(e)}")
    st.stop()
except Exception as e:
    st.error(f"Kritik Başlangıç Hatası (import): {repr(e)}")
    st.stop()
# ===========================================

# Other imports
try:
    from chromadb import Client, Settings
    from chromadb.api.models.Collection import Collection
    print("--- chromadb imported successfully ---")
except ImportError as e: st.error(f"Kritik Import Hatası: chromadb yüklenemedi. {repr(e)}"); st.stop()
try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    print("--- langchain_google_genai imported successfully ---")
except ImportError as e: st.error(f"Kritik Import Hatası: langchain_google_genai yüklenemedi. {repr(e)}"); st.stop()
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    print("--- langchain_text_splitters imported successfully ---")
except ImportError as e: st.error(f"Kritik Import Hatası: langchain_text_splitters yüklenemedi. {repr(e)}"); st.stop()
try:
    from langchain_community.document_loaders import PyPDFLoader
    print("--- langchain_community.document_loaders imported successfully ---")
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
# ===========================================
# CACHE YENİDEN ETKİNLEŞTİRİLDİ
@st.cache_resource
# ===========================================
def setup_rag_components():
    """Tüm RAG bileşenlerini başlatır ve cache'ler."""
    print("--- DEBUG: setup_rag_components ÇALIŞTIRILIYOR (cache ile)... ---") # Cache'lendiğinde bu bir daha görünmemeli
    try:
        gen
