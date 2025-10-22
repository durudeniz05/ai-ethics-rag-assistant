# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (SON VE HATASIZ SÜRÜM - Cache Debugging)
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
    print("--- google.generativeai başarıyla import edildi ---")
    genai = google.generativeai

    APIError_class = None
    if hasattr(genai, 'errors') and hasattr(genai.errors, 'APIError'):
        APIError_class = genai.errors.APIError
        print(f"--- APIError genai.errors altından bulundu: {APIError_class} ---")
    elif hasattr(genai, 'APIError'):
         APIError_class = genai.APIError
         print(f"--- APIError genai altından bulundu: {APIError_class} ---")

    if APIError_class is None:
        print("!!! APIError sınıfı genai veya genai.errors altında bulunamadı !!!")
        APIError = Exception # Fallback
    else:
        APIError = APIError_class
        print(f"--- APIError başarıyla atandı: {APIError} ---")

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

# Diğer importlar
try:
    from chromadb import Client, Settings
    print("--- chromadb başarıyla import edildi ---")
except ImportError as e:
    print(f"!!! chromadb import edilemedi: {e} !!!")
    st.error(f"Kritik Import Hatası: chromadb yüklenemedi. {e}")
    st.stop()

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    print("--- langchain_google_genai başarıyla import edildi ---")
except ImportError as e:
    print(f"!!! langchain_google_genai import edilemedi: {e} !!!")
    st.error(f"Kritik Import Hatası: langchain_google_genai yüklenemedi. {e}")
    st.stop()

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    print("--- langchain_text_splitters başarıyla import edildi ---")
except ImportError as e:
    print(f"!!! langchain_text_splitters import edilemedi: {e} !!!")
    st.error(f"Kritik Import Hatası: langchain_text_splitters yüklenemedi. {e}")
    st.stop()

try:
    from langchain_community.document_loaders import PyPDFLoader
    print("--- langchain_community.document_loaders başarıyla import edildi ---")
except ImportError as e:
    print(f"!!! langchain_community.document_loaders import edilemedi: {e} !!!")
    st.error(f"Krit
