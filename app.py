# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (SON VE HATASIZ SÜRÜM - ChromaDB Debugging)
# =================================================================================

import streamlit as st
import os
import glob
import tempfile
import textwrap
import traceback # Import traceback at the top

# RAG Bileşenleri
# ===========================================
# IMPORT DEBUGGING BLOĞU
try:
    import google.generativeai
    # print("--- google.generativeai başarıyla import edildi ---") # Logları temiz tutalım
    genai = google.generativeai

    APIError_class = None
    if hasattr(genai, 'errors') and hasattr(genai.errors, 'APIError'):
        APIError_class = genai.errors.APIError
        # print(f"--- APIError genai.errors altından bulundu: {APIError_class} ---")
    elif hasattr(genai, 'APIError'):
         APIError_class = genai.APIError
         # print(f"--- APIError genai altından bulundu: {APIError_class} ---")

    if APIError_class is None:
        print("!!! APIError sınıfı genai veya genai.errors altında bulunamadı !!!")
        APIError = Exception # Fallback
    else:
        APIError = APIError_class
        # print(f"--- APIError başarıyla atandı: {APIError} ---")

except ImportError as e:
    print(f"!!! google.generativeai import edilemedi:")
    print(repr(e))
    st.error(f"Kritik Import Hatası: google.generativeai yüklenemedi. Detay: {repr(e)}")
    st.stop()
except AttributeError as e:
    print(f"!!! genai.errors bulunamadı veya APIError aranırken hata: {e} !!!")
    APIError = Exception
    print("--- APIError için genel Exception kullanılacak ---")
except Exception as e:
    print(f"!!! Import sırasında beklenmedik hata:")
    print(repr(e))
    st.error(f"Kritik Başlangıç Hatası. Detay: {repr(e)}")
    st.stop()
# ===========================================

from chromadb import Client, Settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader


# --- 1. API Anahtarını ve Bileşenleri Hazırlama ---

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("HATA: Streamlit Secrets'ta 'GEMINI_API_KEY' bulunamadı. Lütfen kontrol edin.")
    st.stop()


@st.cache_resource
def setup_rag_components():
    """Gemini Client, Embedding Modeli, Text Splitter ve Chroma Collection'ı hazırlar."""
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        embedding_model_name = "models/text-embedding-004"
        embedding_function = GoogleGenerativeAIEmbeddings(
            model=embedding_model_name,
            google_api_key=GEMINI_API_KEY
        )
    except Exception as e:
        st.error(f"KRİTİK HATA: Gemini API Bağlantı Sorunu. Detay: {e}")
        st.stop()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    # ===========================================
    # CHROMA KISMINI GEÇİCİ OLARAK YORUM SATIRI YAP
    collection = None # Başlangıç değeri None
    print("--- DEBUG: ChromaDB geçici olarak devre dışı bırakıldı ---") # Loga yazdır
    # try:
    #     import chromadb
    #     print("--- DEBUG: chromadb import edildi ---")
    #     chroma_client = chromadb.Client()
    #     print("--- DEBUG: chromadb.Client() oluşturuldu ---")
    #     collection_name = "ai_ethics_manual_collection"
    #     try:
    #         print(f"--- DEBUG: '{collection_name}' siliniyor (varsa)... ---")
    #         chroma_client.delete_collection(name=collection_name)
    #         print(f"--- DEBUG: '{collection_name}' silindi. ---")
    #     except Exception as del_e:
    #         print(f"--- DEBUG: Koleksiyon silme hatası (yok sayılıyor): {del_e} ---")
    #         pass
    #     print(f"--- DEBUG: '{collection_name}' oluşturuluyor/alınıyor... ---")
    #     collection = chroma_client.get_or_create_collection(name=collection_name)
    #     print(f"--- DEBUG: Collection objesi alındı: {collection} ---")
    # except Exception as e:
    #     print(f"!!! ChromaDB başlatılırken HATA: {e} !!!")
    #     st.error(f"ChromaDB başlatılamadı: {e}"); st.stop()
    # ===========================================


    llm = genai.GenerativeModel('gemini-1.5-flash')
    # Collection'ı (muhtemelen None) döndür
    return llm, embedding_function, text_splitter, collection

# --- 2. Veri İşleme ve Vektör Kaydetme Fonksiyonu ---
# Bu fonksiyon collection None ise hata verecektir, şimdilik önemli değil
# Sadece uygulamanın açılıp açılmadığını test ediyoruz.
def index_documents(uploaded_files, collection, text_splitter, embedding_function):
    """Yüklenen dosyaları işler ve Vektör Veritabanı'na kaydeder."""
    # Collection None ise işlem yapma (DEBUG için)
    if collection is None:
        st.warning("DEBUG: Collection (Veritabanı) devre dışı olduğu için indexleme yapılamıyor.")
        return 0, 0

    st.info(f"{len(uploaded_files)} dosya işleniyor...")
