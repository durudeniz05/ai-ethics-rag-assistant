# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (SON VE HATASIZ SÜRÜM)
# =================================================================================

import streamlit as st
import os
import glob
import tempfile
import textwrap

# RAG Bileşenleri
from google import genai
from google.genai.errors import APIError
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
        # Gemini Client (LLM)
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Embedding Modeli (Vektörleştirme)
        embedding_model_name = "text-embedding-004"
        embedding_function = GoogleGenerativeAIEmbeddings(
            model=embedding_model_name,
            api_key=GEMINI_API_KEY
        )
    except Exception as e:
        # API bağlantısında bir hata olursa, ekranı çökertmek yerine mesaj gösterir
        st.error(f"KRİTİK HATA: Gemini API Bağlantı Sorunu. Anahtarınızı ve Streamlit Secrets'ı kontrol edin. Detay: {e}")
        st.stop()
        
    # 2. Metin Parçalayıcı
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    
    # 3. Chroma Client (Vektör DB)
    chroma_client = Client(Settings(allow_reset=True))
    collection_name = "ai_ethics_manual_collection"
    
    # Collection'ı temizle ve yeniden oluştur
    try:
        chroma_client.delete_collection(name=collection_name)
    except:
        pass 
        
    collection = chroma_client.get_or_create_collection(name=collection_name)
        
    return gemini_client, embedding_function, text_splitter, collection


# --- 2. Veri İşleme ve Vektör Kaydetme Fonksiyonu ---

def index_documents(uploaded_files, collection, text_splitter, embedding_function):
    """Yüklenen dosyaları işler ve Vektör Veritabanı'na kaydeder."""
    
    chunked_texts = []
    chunk_metadatas = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for uploaded_file in uploaded_files:
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.get_buffer())
            
            loader = PyPDFLoader(temp_file_path)
            documents = loader.load()
            chunks = text_splitter.split_documents(documents)

            for chunk in chunks:
                chunked_texts.append(chunk.page_content)
                chunk_metadatas.append({"source": uploaded_file.name})

    if not chunked_texts:
        st.error("Yüklenen dosyalardan metin çıkarılamadı.")
        return 0

    # 4. Parçaları Embedding'e Çevirme
    try:
        with st.spinner("Dokümanlar işleniyor ve vektörlere çevriliyor..."):
            embeddings = embedding_function.embed_documents(chunked_texts) 
    except Exception as e:
        st.error(f"Embedding Hatası: Vektör oluşturulurken API'ye eriş
