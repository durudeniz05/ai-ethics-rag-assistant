# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (Final Sürüm - APIError Güncel Versiyona Uyarlandı)
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
    # DÜZELTME: Güncel google-generativeai (0.7.2) paketi için doğru import şekli
    from google.generativeai import APIError 
    
    print("--- google.generativeai and APIError imported successfully ---")
except ImportError as e: 
    st.error(f"Kritik Import Hatası: google.generativeai veya APIError yüklenemedi. {repr(e)}"); st.stop()
except Exception as e: 
    st.error(f"Kritik Başlangıç Hatası (google import): {repr(e)}"); st.stop()
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
except KeyError: st.error("HATA: Streamlit Secrets'ta 'GEMINI_API_KEY' bulunamadı."); st.stop()
except Exception as e: st.error(f"Secrets okunurken HATA: {e}"); st.stop()

# --- 2. Setup Components (Cache Enabled) ---
@st.cache_resource 
def setup_rag_components():
    """Tüm RAG bileşenlerini başlatır ve cache'ler."""
    print("--- DEBUG: setup_rag_components ÇALIŞTIRILIYOR (cache ile)... ---")
    llm, embedding_function, text_splitter, collection = None, None, None, None 

    # --- Start Main Try Block ---
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
            raise chroma_e 
            
        # LLM Model
        llm = genai.GenerativeModel('gemini-1.5-flash')

        print("--- DEBUG: setup_rag_components BAŞARIYLA TAMAMLANDI (cache ile) ---")
        return llm, embedding_function, text_splitter, collection

    # --- End Main Try Block ---
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
                    if hasattr(chunk, 'metadata') and 'page' in chunk.metadata: 
                        metadata['page'] = chunk.metadata['page']
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
        with st.spinner(f"{len(chunked_texts)} parça vektöre çevriliyor..."): 
            embeddings = embedding_function.embed_documents(chunked_texts)
    except Exception as e: st.error(f"Embedding Hatası: Vektör oluşturulamadı. Detay: {e}"); return processed_files_count, 0
    
    ids = [f"doc_{i}" for i in range(len(chunked_texts))]
    
    try:
        with st.spinner("Vektör veritabanına ekleniyor..."): 
            collection.add(documents=chunked_texts, embeddings=embeddings, metadatas=chunk_metadatas, ids=ids)
        return processed_files_count, len(chunked_texts)
    except Exception as e: 
        st.error(f"Vektör DB ekleme hatası: {e}"); st.error(traceback.format_exc()); 
        return processed_files_count, 0

# --- 4. RAG Sorgulama Fonksiyonu ---
def ask_rag_assistant(question, llm, collection, embedding_function):
    """RAG sorgusunu çalıştırır ve cevabı döndürür."""
    try:
        # 1. Sorguyu vektöre çevir
        with st.spinner("Sorunuz analiz ediliyor..."): 
            query_vector = embedding_function.embed_query(question)
            
        # 2. Vektör veritabanında en yakın parçaları bul
        with st.spinner("İlgili dokümanlar aranıyor..."): 
            results = collection.query(query_embeddings=[query_vector], n_results=3, include=['metadatas', 'documents'])
            
        # Sonuç kontrolü
        if not results or not results.get('ids') or not results['ids'][0]: 
            return "Veritabanında sorunuzla ilgili bilgi bulunamadı."
        
        # 3. Bağlamı oluştur (Noktalı virgül kaldırıldı, girintisi düzeltildi)
        retrieved_chunks = results['documents'][0]
        retrieved_metadatas = results['metadatas'][0]
        context = "\n---\n".join(retrieved_chunks)
        
        # 4. Prompt'u oluştur ve LLM'e gönder
        system_prompt = (
            "Sen bir Yapay Zeka Etiği ve Uyum asistanısın. Yalnızca sağlanan bağlamdaki bilgilere dayanarak yanıtla. "
            "Eğer bağlamda bilgi yoksa 'Elimdeki dokümanlarda bu konuyla ilgili spesifik bilgi bulunmamaktadır.' diye cevap ver. "
            "Cevabını kısa ve öz tut. Cevabın sonunda, kullanılan kaynağı '[Kaynak: Dosya Adı, Sayfa X]' formatında belirt."
        )
        full_prompt = f"{system_prompt}\n\nBağlam:\n{context}\n\nSoru: {question}\n\nCevap:"
        
        with st.spinner("Cevap oluşturuluyor..."): 
            response = llm.generate_content(full_prompt)
        
        # 5. Kaynak bilgisini hazırla
        source_info = []
        if retrieved_metadatas:
            for meta in retrieved_metadatas:
                if meta: 
                    source, page = meta.get('source', '?'), meta.get('page', None)
                    source_info.append(f"{source}, Sayfa {page + 1}" if page is not None else source)
        unique_source_info = sorted(list(set(source_info)))
        
        # 6. Cevabı al ve Hata/Güvenlik durumunu ele al
        try: 
            final_answer = response.text
        except ValueError as e:
             final_answer = f"Model uygun cevap üretemedi. Detay: {repr(e)}"
             try:
                 if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                      final_answer += f" (Sebep: {response.prompt_feedback.block_reason.name if response.prompt_feedback.block_reason else 'Bilinmiyor'})"
             except AttributeError: pass
             
        # 7. Kaynağı cevaba ekle
        if unique_source_info and not any(src.split(',')[0] in final_answer for src in unique_source_info): 
            final_answer += f" [Kaynak: {'; '.join(unique_source_info)}]"
        
        return final_answer
        
    except APIError as e: 
        return f"API HATA: Gemini servisine erişim sağlanamadı. Detay: {repr(e)}"
    except Exception as e: 
        st.error(f"RAG Sorgulama Hatası: {e}"); st.error(traceback.format_exc()); 
        return f"GENEL HATA: RAG sorgusu işlenirken bir sorun oluştu."

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
        st.stop() 

    # Bileşenlerin başarıyla yüklenip yüklenmediğini kontrol et
    if not llm or not embedding_function or not text_splitter or not collection:
          st.error("Bileşenlerden biri veya birkaçı yüklenemedi. Lütfen logları ve API key ayarlarını kontrol edin.")
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
            doc_count = collection.count()
            st.info(f"Vektör Veritabanında Kayıtlı Parça: {doc_count}")
        except Exception as e:
            doc_count = 0; st.info(f"Vektör Veritabanında Kayıtlı Parça: {doc_count}")

    # Chat Arayüzü
    if "messages" not in st.session_state: 
        st.session_state.messages = [{"role": "assistant", "content": "Merhaba! Lütfen sol panelden PDF'lerinizi yükleyip işleyin ve sohbeti başlatın."}]
    
    for msg in st.session_state.messages: 
        st.chat_message(msg["role"]).write(msg["content"])
        
    if prompt := st.chat_input("Sorunuzu buraya yazın..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        try: current_doc_count = collection.count()
        except Exception: current_doc_count = 0
        
        if current_doc_count == 0: 
            response = "Veritabanında işlenmiş doküman yok. Lütfen önce doküman yükleyin ve 'Dokümanları İşle ve Kaydet' butonuna basın."
            st.chat_message("assistant").warning(response) 
        else:
            with st.chat_message("assistant"): 
                response = ask_rag_assistant(prompt, llm, collection, embedding_function)
                st.write(response)
                
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
