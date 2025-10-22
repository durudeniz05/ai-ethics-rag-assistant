# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (Final Sürüm - Final Syntax Fix 3)
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

# Other imports (Corrected try-except structure)
# ===========================================
try: # Try block for chromadb
    from chromadb import Client, Settings
    from chromadb.api.models.Collection import Collection
    # print("--- chromadb imported successfully ---")
except ImportError as e: # Except block aligned with try
    print(f"!!! FAILED to import chromadb:")
    print(repr(e))
    st.error(f"Critical Import Error: Failed to load chromadb. Details: {repr(e)}")
    st.stop()

try: # Try block for langchain_google_genai
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    # print("--- langchain_google_genai imported successfully ---")
except ImportError as e: # Except block aligned with try
    print(f"!!! FAILED to import langchain_google_genai:")
    print(repr(e))
    st.error(f"Critical Import Error: Failed to load langchain_google_genai. Details: {repr(e)}")
    st.stop()

try: # Try block for langchain_text_splitters
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    # print("--- langchain_text_splitters imported successfully ---")
except ImportError as e: # Except block aligned with try
    print(f"!!! FAILED to import langchain_text_splitters:")
    print(repr(e))
    # ===========================================
    # SYNTAX ERROR FIX HERE
    st.error(f"Critical Import Error: Failed to load langchain_text_splitters. Details: {repr(e)}") # Added ')'
    # ===========================================
    st.stop()

try: # Try block for langchain_community
    from langchain_community.document_loaders import PyPDFLoader
    # print("--- langchain_community.document_loaders imported successfully ---")
except ImportError as e: # Except block aligned with try
    print(f"!!! FAILED to import langchain_community.document_loaders:")
    print(repr(e))
    st.error(f"Critical Import Error: Failed to load langchain_community.document_loaders. Details: {repr(e)}")
    st.stop()
# ===========================================


# --- 1. API Key ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError: st.error("HATA: Streamlit Secrets'ta 'GEMINI_API_KEY' bulunamadı."); st.stop()
except Exception as e: st.error(f"Secrets okunurken HATA: {e}"); st.stop()

# --- 2. Setup Components (Cache Enabled) ---
@st.cache_resource # Cache etkin
def setup_rag_components():
    """Tüm RAG bileşenlerini başlatır ve cache'ler."""
    print("--- DEBUG: setup_rag_components ÇALIŞTIRILIYOR (cache ile)... ---")
    llm, embedding_function, text_splitter, collection = None, None, None, None # Initialize
    try: # Start main try block
        genai.configure(api_key=GEMINI_API_KEY)
        embedding_model_name = "models/text-embedding-004"
        embedding_function = GoogleGenerativeAIEmbeddings(
            model=embedding_model_name,
            google_api_key=GEMINI_API_KEY
        )
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        # ChromaDB (In-Memory)
        try:
            import chromadb
            chroma_client = chromadb.Client()
            collection_name = "ai_ethics_manual_collection"
            try: chroma_client.delete_collection(name=collection_name)
            except: pass
            collection = chroma_client.get_or_create_collection(name=collection_name)
        except Exception as chroma_e:
            print(f"!!! FAILED during ChromaDB initialization: {chroma_e} !!!")
            print(traceback.format_exc())
            st.error(f"ChromaDB başlatılamadı: {chroma_e}")
            raise chroma_e # Re-raise
        llm = genai.GenerativeModel('gemini-1.5-flash')
        print("--- DEBUG: setup_rag_components BAŞARIYLA TAMAMLANDI (cache ile) ---")
        return llm, embedding_function, text_splitter, collection
    # Aligned except block
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
    global APIError
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
             final_answer = f"Model uygun cevap üretemedi. Detay: {repr(e)}"
             try:
                 if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                     final_answer += f" (Sebep: {response.prompt_feedback})"
             except AttributeError: pass
        if unique_source_info and not any(src.split(',')[0] in final_answer for src in unique_source_info): final_answer += f" [Kaynak: {'; '.join(unique_source_info)}]"
        return final_answer
    except APIError as e: return f"API HATA: Gemini servisine erişim sağlanamadı. Detay: {repr(e)}"
    except Exception as e: st.error(f"RAG Sorgulama Hatası: {e}"); st.error(traceback.format_exc()); return f"GENEL HATA: RAG sorgusu işlenirken bir sorun oluştu."

# =================================================================================
# 5. STREAMLIT ANA FONKSİYON
# =================================================================================

def main():
    st.set_page_config(page_title="AI Ethics RAG Assistant", layout="wide")
    st.title("🤖 AI Ethics & Compliance RAG Assistant")
    st.markdown("Yapay Zeka Etik ve Uyum Dokümanlarına Dayalı Soru-Cevap Asistanı")
    st.caption("Not: Bu uygulama Google Gemini ve ChromaDB kullanmaktadır.")

    # Bileşenleri yükle (Cache ile)
    try:
        llm, embedding_function, text_splitter, collection = setup_rag_components()
    except Exception as e:
        st.stop() # Error already shown/logged in setup_rag_components

    # Bileşenlerin başarıyla yüklenip yüklenmediğini kontrol et
    if not llm or not embedding_function or not text_splitter or not collection:
         st.error("Bileşenlerden biri veya birkaçı yüklenemedi. Logları kontrol edin.")
         st.stop()

    # Sidebar
    with st.sidebar:
        st.header("1. Doküman Yükleme (PDF)")
        uploaded_files = st.file_uploader("AI Etik ve Uyum PDF'lerini yükleyin", type="pdf", accept_multiple_files=True, key="file_uploader")

        if st.button("Dokümanları İşle ve Kaydet"):
            if uploaded_files:
                try:
                    existing_ids = collection.get(include=[])['ids']
                    if existing_ids: collection.delete(ids=existing_ids); st.info("Mevcut veritabanı temizlendi.")
                except Exception as e: pass
                processed_count, chunk_count = index_documents(uploaded_files, collection, text_splitter, embedding_function)
                if chunk_count > 0:
                    st.success(f"Başarıyla {processed_count}/{len(uploaded_files)} dosya işlendi ve {chunk_count} parça kaydedildi.")
                st.rerun()
            else:
                st.warning("Lütfen işlem yapmak için bir PDF dosyası yükleyin.")

        # Mevcut Kayıt Sayısı
        try:
            doc_count
