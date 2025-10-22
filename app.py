# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (SON VE HATASIZ SÜRÜM - Import düzeltmesi yapıldı)
# =================================================================================

import streamlit as st
import os
import glob
import tempfile
import textwrap

# RAG Bileşenleri
# ===========================================
# IMPORT DÜZELTMESİ BURADA YAPILDI
import google.generativeai as genai
from google.generativeai.errors import APIError
# ===========================================
from chromadb import Client, Settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader


# --- 1. API Anahtarını ve Bileşenleri Hazırlama ---

# API Anahtarını Streamlit Secrets'tan alıyoruz
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    # Bu hata oluşursa, uygulamayı durdurur ve kullanıcıya mesaj gösterir
    st.error("HATA: Streamlit Secrets'ta 'GEMINI_API_KEY' bulunamadı. Lütfen kontrol edin.")
    st.stop()


@st.cache_resource
def setup_rag_components():
    """Gemini Client, Embedding Modeli, Text Splitter ve Chroma Collection'ı hazırlar."""

    # 1. API Bağlantılarını Hata Yakalama İçinde Başlatma
    try:
        # Gemini Client (LLM) - DİKKAT: Artık 'genai.' ön ekini kullanıyoruz
        # client = genai.Client(...) yerine genai.configure(...) kullanılabilir veya doğrudan model oluşturulabilir.
        # Dokümantasyona göre bu versiyonda genai.configure() öneriliyor.
        genai.configure(api_key=GEMINI_API_KEY)

        # Embedding Modeli (Vektörleştirme)
        embedding_model_name = "text-embedding-004" # Bu model adı hala geçerli olabilir, kontrol edin.
        embedding_function = GoogleGenerativeAIEmbeddings(
            model=embedding_model_
