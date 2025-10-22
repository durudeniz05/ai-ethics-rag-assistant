# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (Final Sürüm - Import & Syntax Fix Son)
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
    # APIError İÇİN DOĞRU IMPORT KULLANILDI (errors altından)
    from google.generativeai.errors import APIError
    # ===========================================
    print("--- google.generativeai and APIError imported successfully ---")
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
    print("--- DEBUG: setup_rag_components ÇALIŞTIRILIYOR (cache ile)... ---")
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
        try: chroma_client.delete_collection(name=collection_name)
        except: pass
        # ===========================================
        # SYNTAX ERROR FIX HERE
        collection = chroma_client.get_or_create_collection(name=collection_name) # Added ')'
        # ===========================================

        # LLM Model
        llm = genai.GenerativeModel('gemini-1.5-flash')

        print("--- DEBUG: setup_rag_components BAŞARIYLA TAMAMLANDI (cache ile) ---")
        return llm, embedding_function, text_splitter, collection

    except Exception as e:
        print(f"!!! setup_rag_components içinde HATA (cache ile): {e} !!!")
        print(traceback.format_exc())
        st.error(f"Uygulama bileşenleri başlatılırken bir hata oluştu. Detaylar loglarda. Hata: {e}")
        raise e

# --- 3. Veri İşleme Fonksiyonu ---
def index_documents(uploaded_files, collection, text_splitter, embedding_function):
    """Yüklenen dosyaları işler ve Vektör Veritabanı'na kaydeder."""
    chunked_texts, chunk_metadatas, processed_files_count = [], [], 0
    with tempfile.TemporaryDirectory() as temp_dir:
        for uploaded_file in uploaded_files:
            file_processed = False; temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            try:
                with open(temp_file_path, "wb") as f: f.write(uploaded_file.getbuffer())
                loader = PyPDFLoader(temp_file_path); documents = loader.load()
                if not documents: st.warning(f"'{uploaded_file.name}' içerik okunamadı."); continue
                chunks = text_splitter.split_documents(documents)
                if not chunks: st.warning(f"'{uploaded_file.name}' parçalara ayrılamadı."); continue
                for chunk in chunks:
                    chunked_texts.append(chunk.page_content)
                    metadata = {"source": uploaded_file.name}
                    if hasattr(chunk, 'metadata') and 'page' in chunk.metadata: metadata['page'] = chunk.metadata['page']
                    chunk_metadatas.append(metadata)
                file_processed = True
            except Exception as e: st.error(f"'{uploaded_file.name}' işlenirken hata: {e}"); st.error(traceback.format_exc())
            finally:
                if file_processed: processed_files_count += 1
                if os.path.exists(temp_file_path):
                    try: os.remove(temp_file_path)
                    except OSError as e: pass
    if not chunked_texts: st.error("Yüklenen geçerli PDF dosyalarından metin çıkarılamadı."); return 0, 0
    try:
        with st.spinner(f"{len(chunked_texts)} parça vektöre çevriliyor..."): embeddings = embedding_function.embed_documents(chunked_texts)
    except Exception as e: st.error(f"Embedding Hatası: Vektör oluşturulamadı. Detay: {e}"); return processed_files_count, 0
    ids = [f"doc_{i}" for i in range(len(chunked_texts))]
    try:
        with st.spinner("Vektör veritabanına ekleniyor..."): collection.add(documents=chunked_texts, embeddings=embeddings, metadatas=chunk_metadatas, ids=ids)
        return processed_files_count, len(chunked_texts)
    except Exception as e: st.error(f"Vektör DB ekleme hatası: {e}"); st.error(traceback.format_exc()); return processed_files_count, 0

# --- 4. RAG Sorgulama Fonksiyonu ---
def ask_rag_assistant(question, llm, collection, embedding_function):
    """RAG sorgusunu çalıştırır ve cevabı döndürür."""
    global APIError # Use the APIError class found during import
    try:
        with st.spinner("Sorunuz analiz ediliyor..."): query_vector = embedding_function.embed_query(question)
        with st.spinner("İlgili dokümanlar aranıyor..."): results = collection.query(query_embeddings=[query_vector], n_results=3, include=['metadatas', 'documents'])
        if not results or not results.get('ids') or not results['ids'][0]: return "Veritabanında sorunuzla ilgili bilgi bulunamadı."
        retrieved_chunks = results['documents'][0]; retrieved_metadatas = results['metadatas'][0]
        context = "\n---\n".join(retrieved_chunks)
        system_prompt = ("Sen bir Yapay Zeka Etiği ve Uyum asistanısın. Yalnızca sağlanan bağlamdaki bilgilere dayanarak yanıtla. Eğer bağlamda bilgi yoksa 'Elimdeki dokümanlarda bu konuyla ilgili spesifik bilgi bulunmamaktadır.' diye cevap ver. Cevabını kısa ve öz tut. Cevabın sonunda, kullanılan kaynağı '[Kaynak: Dosya Adı, Sayfa X]' formatında belirt.")
        full_prompt = f"{system_prompt}\n\nBağlam:\n{context}\n\nSoru: {question}\n\nCevap:"
        with st.spinner("Cevap oluşturuluyor..."): response = llm.generate_content(full_prompt)
        source_info = []
        if retrieved_metadatas:
            for meta in retrieved_metadatas:
                if meta: source, page = meta.get('source', '?'), meta.get('page', None); source_info.append(f"{source}, Sayfa {page + 1}" if page is not None else source)
        unique_source_info = sorted(list(set(source_info)))
        try: final_answer = response.text
        except ValueError as e:
             final_answer = f"Model uygun
