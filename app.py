# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (SON VE HATASIZ SÜRÜM - Final SyntaxError Fix)
# =================================================================================

import streamlit as st
import os
import glob
import tempfile
import textwrap
import traceback # Import traceback at the top

# RAG Bileşenleri
# ===========================================
# IMPORT DEBUGGING BLOĞU (SyntaxError fixes included)
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
        APIError = Exception
    else:
        APIError = APIError_class

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
    # ===========================================
    # SYNTAX ERROR FIX HERE
    print(f"!!! Import sırasında beklenmedik hata:")
    print(repr(e)) # Print the error representation safely
    st.error(f"Kritik Başlangıç Hatası. Detay: {repr(e)}")
    # ===========================================
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

    try:
        import chromadb
        chroma_client = chromadb.Client()
        collection_name = "ai_ethics_manual_collection"
        try: chroma_client.delete_collection(name=collection_name)
        except: pass
        collection = chroma_client.get_or_create_collection(name=collection_name)
    except Exception as e:
        st.error(f"ChromaDB başlatılamadı: {e}"); st.stop()

    llm = genai.GenerativeModel('gemini-2.5-flash')
    return llm, embedding_function, text_splitter, collection

# --- 2. Veri İşleme ve Vektör Kaydetme Fonksiyonu ---

def index_documents(uploaded_files, collection, text_splitter, embedding_function):
    """Yüklenen dosyaları işler ve Vektör Veritabanı'na kaydeder."""
    chunked_texts, chunk_metadatas, processed_files_count = [], [], 0
    with tempfile.TemporaryDirectory() as temp_dir:
        for uploaded_file in uploaded_files:
            file_processed = False; temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            try:
                with open(temp_file_path, "wb") as f: f.write(uploaded_file.getbuffer())
                loader = PyPDFLoader(temp_file_path); documents = loader.load()
                if not documents: continue
                chunks = text_splitter.split_documents(documents)
                if not chunks: continue
                for chunk in chunks:
                    chunked_texts.append(chunk.page_content)
                    metadata = {"source": uploaded_file.name}
                    if hasattr(chunk, 'metadata') and 'page' in chunk.metadata: metadata['page'] = chunk.metadata['page']
                    chunk_metadatas.append(metadata)
                file_processed = True
            except Exception as e: st.error(f"'{uploaded_file.name}' dosyası işlenirken hata: {e}")
            finally:
                if file_processed: processed_files_count += 1
                if os.path.exists(temp_file_path):
                    try: os.remove(temp_file_path)
                    except OSError as e: pass
    if not chunked_texts: return 0, 0
    try:
        with st.spinner(f"..."): embeddings = embedding_function.embed_documents(chunked_texts)
    except Exception as e: st.error(f"Embedding Hatası: ... Detay: {e}"); return processed_files_count, 0
    ids = [f"doc_{i}" for i in range(len(chunked_texts))]
    try:
        collection.add(documents=chunked_texts, embeddings=embeddings, metadatas=chunk_metadatas, ids=ids)
        return processed_files_count, len(chunked_texts)
    except Exception as e: st.error(f"Vektör DB ekleme hatası: {e}"); return processed_files_count, 0

# --- 3. RAG Sorgulama Fonksiyonu ---

def ask_rag_assistant(question, llm, collection, embedding_function):
    """RAG sorgusunu çalıştırır ve cevabı döndürür."""
    global APIError
    try:
        with st.spinner("..."): query_vector = embedding_function.embed_query(question)
        with st.spinner("..."): results = collection.query(query_embeddings=[query_vector], n_results=3, include=['metadatas', 'documents'])
        if not results or not results.get('ids') or not results['ids'][0]: return "..."
        retrieved_chunks = results['documents'][0]; retrieved_metadatas = results['metadatas'][0]
        context = "\n---\n".join(retrieved_chunks)
        system_prompt = ("Sen bir Yapay Zeka Etiği ve Uyum asistanısın...")
        full_prompt = f"{system_prompt}\n\nBağlam:\n{context}\n\nSoru: {question}\n\nCevap:"
        with st.spinner("..."): response = llm.generate_content(full_prompt)
        source_info = []
        if retrieved_metadatas:
            for meta in retrieved_metadatas:
                if meta: source, page = meta.get('source', '?'), meta.get('page', None); source_info.append(f"{source}, Sayfa {page + 1}" if page is not None else source)
        unique_source_info = sorted(list(set(source_info)))
        try: final_answer = response.text
        except ValueError as e:
             final_answer = f"Model uygun cevap üretemedi. Detay: {e}"
             try:
                 if response.prompt_feedback: final_answer += f" (Sebep: {response.prompt_feedback})"
             except AttributeError: pass
        if unique_source_info and not any(src.split(',')[0] in final_answer for src in unique_source_info): final_answer += f" [Kaynak: {'; '.join(unique_source_info)}]"
        return final_answer
    except APIError as e: return f"API HATA: ... Detay: {e}"
    except Exception as e:
        st.error(f"RAG Sorgulama Hatası: {e}"); st.error(traceback.format_exc())
        return f"GENEL HATA: ... Detaylar loglarda."

# =================================================================================
# 4. STREAMLIT ANA FONKSİYON
# =================================================================================

def main():
    st.set_page_config(page_title="AI Ethics RAG Assistant", layout="wide")
    st.title("🤖 AI Ethics & Compliance RAG Assistant")
    st.markdown("..."); st.caption("...")
    try: llm, embedding_function, text_splitter, collection = setup_rag_components()
    except Exception as e: st.error(f"... Kurulum hatası: {e}"); st.stop()
    with st.sidebar:
        st.header("1. Doküman Yükleme (PDF)")
        uploaded_files = st.file_uploader("...", type="pdf", accept_multiple_files=True, key="file_uploader")
        if 'processing_done' not in st.session_state: st.session_state.processing_done = False
        if st.button("Dokümanları İşle ve Kaydet"):
            st.session_state.processing_done = False
            if uploaded_files:
                try:
                    existing_ids = collection.get(include=[])['ids']
                    if existing_ids: collection.delete(ids=existing_ids); st.info("...")
                except Exception as e: pass
                processed_count, chunk_count = index_documents(uploaded_files, collection, text_splitter, embedding_function)
                if chunk_count > 0: st.success(f"Başarıyla {processed_count}/{len(uploaded_files)} dosya işlendi..."); st.session_state.processing_done = True
                st.rerun()
            else: st.warning("...")
        try: doc_count = collection.count(); st.info(f"... Kayıtlı Parça: {doc_count}")
        except Exception as e: doc_count = 0; st.info(f"... Kayıtlı Parça: {doc_count}")
    if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Merhaba! ..."}]
    for msg in st.session_state.messages: st.chat_message(msg["role"]).write(msg["content"])
    if prompt := st.chat_input("..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        try: current_doc_count = collection.count()
        except Exception: current_doc_count = 0
        if current_doc_count == 0: response = "Veritabanında doküman yok..."; st.warning(response)
        else:
            with st.chat_message("assistant"): response = ask_rag_assistant(prompt, llm, collection, embedding_function); st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()

