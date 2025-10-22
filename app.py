# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (SON VE HATASIZ SÜRÜM - Import ve Syntax düzeltmesi)
# =================================================================================

import streamlit as st
import os
import glob
import tempfile
import textwrap

# RAG Bileşenleri
import google.generativeai as genai
from google.generativeai import APIError
from chromadb import Client, Settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader


# --- 1. API Anahtarını ve Bileşenleri Hazırlama ---

# API Anahtarını Streamlit Secrets'tan alıyoruz
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("HATA: Streamlit Secrets'ta 'GEMINI_API_KEY' bulunamadı. Lütfen kontrol edin.")
    st.stop()


@st.cache_resource
def setup_rag_components():
    """Gemini Client, Embedding Modeli, Text Splitter ve Chroma Collection'ı hazırlar."""

    # 1. API Bağlantılarını Hata Yakalama İçinde Başlatma
    try:
        genai.configure(api_key=GEMINI_API_KEY)

        # Embedding Modeli (Vektörleştirme)
        embedding_model_name = "text-embedding-004"
        embedding_function = GoogleGenerativeAIEmbeddings(
            model=embedding_model_name,
            google_api_key=GEMINI_API_KEY
        ) # <-- SYNTAX HATASI BURADA DÜZELTİLDİ

    except Exception as e:
        st.error(f"KRİTİK HATA: Gemini API Bağlantı Sorunu. Anahtarınızı ve Streamlit Secrets'ı kontrol edin. Detay: {e}")
        st.stop()

    # 2. Metin Parçalayıcı
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    # 3. Chroma Client (Vektör DB)
    # Güncel chromadb sürümleri için Settings kullanımı değişmiş olabilir.
    # Eğer hata alırsanız, client = chromadb.Client() veya persistent client

