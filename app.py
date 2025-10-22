# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (SON VE HATASIZ SÜRÜM - SyntaxError Fix)
# =================================================================================

import streamlit as st
import os
import glob
import tempfile
import textwrap

# RAG Bileşenleri
# ===========================================
# IMPORT DEBUGGING BLOĞU (SyntaxError fix included)
try:
    import google.generativeai
    print("--- google.generativeai başarıyla import edildi ---")
    print(dir(google.generativeai)) # Modülün içindekileri yazdır
    genai = google.generativeai # genai adını manuel olarak atayalım

    # APIError'ı dinamik olarak bulmaya çalışalım (varsa)
    APIError_class = None
    if hasattr(genai, 'errors') and hasattr(genai.errors, 'APIError'):
        APIError_class = genai.errors.APIError
        print(f"--- APIError genai.errors altından bulundu: {APIError_class} ---")
    elif hasattr(genai, 'APIError'):
         APIError_class = genai.APIError
         print(f"--- APIError genai altından bulundu: {APIError_class} ---")

    if APIError_class is None:
        print("!!! APIError sınıfı genai veya genai.errors altında bulunamadı !!!")
        # Geçici olarak genel Exception kullanalım ki kod çalışsın
        APIError = Exception
    else:
        APIError = APIError_class # Assign the found class to the global name

except ImportError as e:
    # ===========================================
    # SYNTAX ERROR FIX HERE
    print(f"!!! google.generativeai import edilemedi:")
    print(repr(e)) # Print the error representation safely
    st.error(f"Kritik Import Hatası: google.generativeai yüklenemedi. Detay: {repr(e)}")
    # ===========================================
    st.stop()
except AttributeError as e:
    # This might happen if 'genai.errors' doesn't exist
    print(f"!!! genai.errors bulunamadı veya APIError aranırken hata: {e} !!!")
    APIError = Exception # Fallback
    print("--- APIError için genel Exception kullanılacak ---")

except Exception as e:
    print(f"!!! Import sırasında beklenmedik hata: {e} !!!")
    st.error(f"Kritik Başlangıç Hatası: {e}")
    st.stop()
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
    st.error("HATA: Streamlit Secrets'ta 'GEMINI_API_KEY' bulunamadı. Lütfen kontrol edin.")
    st.stop()


@st.cache_resource
def setup_rag_components():
    """Gemini Client, Embedding Modeli, Text Splitter ve Chroma Collection'ı hazırlar."""

    # 1. API Bağlantılarını Hata Yakalama İçinde Başlatma
    try:
        genai.configure(api_key=GEMINI_API_KEY)

        # Embedding Modeli (Vektörleştirme)
        embedding_model_name = "models/text-embedding-004"
        embedding_function = GoogleGenerativeAIEmbeddings(
            model=embedding_model_name,
            google_api_key=GEMINI_API_KEY
        )

    except Exception as e:
        st.error(f"KRİTİK HATA: Gemini API Bağlantı Sorunu. Anahtarınızı ve Streamlit Secrets'ı kontrol edin. Detay: {e}")
        st.stop()

    # 2. Metin Parçalayıcı
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    # 3. Chroma Client (Vektör DB)
    try:
        import chromadb
        chroma_client = chromadb.Client()
        collection_name = "ai_ethics_manual_collection"
        try:
            chroma_client.delete_collection(name=collection_name)
        except:
            pass
        collection = chroma_client.get_or_create_collection(name=collection_name)
    except Exception as e:
        st.error(f"ChromaDB başlatılamadı: {e}")
        st.stop()


    # LLM Modeli
    llm = genai.GenerativeModel('gemini-1.5-flash')

    return llm, embedding_function, text_splitter, collection


# --- 2. Veri İşleme ve Vektör Kaydetme Fonksiyonu ---

def index_documents(uploaded_files, collection, text_splitter, embedding_function):
    """Yüklenen dosyaları işler ve Vektör Veritabanı'na kaydeder."""

    chunked_texts = []
    chunk_metadatas = []
    processed_files_count = 0

    with tempfile.TemporaryDirectory() as temp_dir:
        for uploaded_file in uploaded_files:
            file_processed = False
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            try:
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                loader = PyPDFLoader(temp_file_path)
                documents = loader.load()
                if not documents:
                    st.warning(f"'{uploaded_file.name}' dosyasından içerik okunamadı.")
                    continue

                chunks = text_splitter.split_documents(documents)
                if not chunks:
                     st.warning(f"'{uploaded_file.name}' dosyası parçalara ayrılamadı.")
                     continue

                for chunk in chunks:
                    chunked_texts.append(chunk.page_content)
                    metadata = {"source": uploaded_file.name}
                    if hasattr(chunk, 'metadata') and 'page' in chunk.metadata:
                        metadata['page'] = chunk.metadata['page']
                    chunk_metadatas.append(metadata)
                file_processed = True

            except Exception as e:
                st.error(f"'{uploaded_file.name}' dosyası işlenirken hata: {e}")
            finally:
                if file_processed:
                    processed_files_count += 1
                if os.path.exists(temp_file_path):
                    try:
                        os.remove(temp_file_path)
                    except OSError as e:
                         st.warning(f"Geçici dosya {temp_file_path} silinirken hata (yok sayılıyor): {e}")


    if not chunked_texts:
        st.error("Yüklenen geçerli PDF dosyalarından metin çıkarılamadı veya işlenemedi.")
        return 0, 0

    # 4. Parçaları Embedding'e Çevirme
    try:
        with st.spinner(f"{len(chunked_texts)} metin parçası vektörlere çevriliyor..."):
            embeddings = embedding_function.embed_documents(chunked_texts)
    except Exception as e:
        st.error(f"Embedding Hatası: Vektör oluşturulurken API'ye erişim sağlanamadı. Detay: {e}")
        return processed_files_count, 0

    # 5. Chroma'ya Kaydetme (Vektörleri de ekleyerek)
    ids = [f"doc_{i}" for i in range(len(chunked_texts))]

    try:
        collection.add(
            documents=chunked_texts,
            embeddings=embeddings,
            metadatas=chunk_metadatas,
            ids=ids
        )
        return processed_files_count, len(chunked_texts)
    except Exception as e
