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
        st.error(f"Embedding Hatası: Vektör oluşturulurken API'ye erişim sağlanamadı. Detay: {e}")
        return 0

    # 5. Chroma'ya Kaydetme (Vektörleri de ekleyerek)
    ids = [f"doc_{i}" for i in range(len(chunked_texts))]
    
    collection.add(
        documents=chunked_texts,
        embeddings=embeddings, 
        metadatas=chunk_metadatas,
        ids=ids
    )
    return len(chunked_texts)


# --- 3. RAG Sorgulama Fonksiyonu ---

def ask_rag_assistant(question, gemini_client, collection, embedding_function):
    """RAG sorgusunu çalıştırır ve cevabı döndürür."""
    try:
        # A. Sorguyu Vektörleştirme
        query_vector = embedding_function.embed_query(question)
        
        # B. Retrieval (Geri Getirme): Chroma DB'de arama
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=3  # En alakalı 3 parçayı getir
        )
        
        retrieved_chunks = results['documents'][0]
        retrieved_metadatas = results['metadatas'][0]
        
        # C. Generation (Cevap Üretme)
        context = "\n---\n".join(retrieved_chunks)
        system_prompt = (
            "Sen bir Yapay Zeka Etiği ve Uyum asistanısın. Yalnızca sağlanan bağlamdaki bilgilere dayanarak yanıtla. "
            "Eğer bağlamda bilgi yoksa 'Elimdeki dokümanlarda bu konuyla ilgili spesifik bilgi bulunmamaktadır.' diye cevap ver. "
            "Cevabını kısa ve öz tut. Cevabın sonunda, kullanılan kaynağı '[Kaynak: Dosya Adı]' formatında belirt."
        )
        
        full_prompt = f"{system_prompt}\n\nBağlam: {context}\n\nSoru: {question}\n\nCevap:"
        
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt
        )

        source_files = list(set([m['source'] for m in retrieved_metadatas]))
        final_answer = response.text
        
        if not any(source in final_answer for source in source_files):
             final_answer += f" [Kaynak: {', '.join(source_files)}]"

        return final_answer
        
    except APIError as e:
        return f"API HATA: Gemini servisine erişim sağlanamadı. Detay: {e}"
    except Exception as e:
        return f"GENEL HATA: {e}"


# =================================================================================
# 4. STREAMLIT ANA FONKSİYON
# =================================================================================

def main():
    st.set_page_config(page_title="AI Ethics & Compliance RAG Assistant", layout="wide")

    st.title("🤖 AI Ethics & Compliance RAG Assistant")
    st.markdown("Yapay Zeka Etik ve Uyum Dokümanlarına Dayalı Soru-Cevap Asistanı")
    st.caption("Not: Bu uygulama, API hatalarını aşmak için manuel RAG kurulumu kullanmaktadır.")

    # RAG bileşenlerini yükle
    gemini_client, embedding_function, text_splitter, collection = setup_rag_components()

    # --- Sol Panelde Dosya Yükleme ---
    with st.sidebar:
        st.header("1. Doküman Yükleme (PDF)")
        
        uploaded_files = st.file_uploader(
            "AI Etik ve Uyum PDF'lerini yükleyin", 
            type="pdf", 
            accept_multiple_files=True
        )

        if st.button("Dokümanları İşle ve Kaydet"):
            if uploaded_files:
                # KRİTİK DÜZELTME: CHROMA SİLME HATASI GİDERİLDİ
                # Bu komut, koleksiyondaki her şeyi siler ve yeni yüklemeye yer açar.
                collection.delete(where={
                    "$and": [
                        {"source": {"$ne": "non_existent_source"}}
                    ]
                }) 
                
                chunk_count = index_documents(uploaded_files, collection, text_splitter, embedding_function)
                if chunk_count > 0:
                    st.success(f"Başarıyla {len(uploaded_files)} dosya işlendi ve {chunk_count} parça kaydedildi.")
            else:
                st.warning("Lütfen işlem yapmak için bir PDF dosyası yükleyin.")
                
        # Mevcut Kayıt Sayısı
        st.info(f"Vektör Veritabanında Kayıtlı Parça: {collection.count()}")

    # --- Ana Chat Arayüzü ---
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Merhaba! Lütfen sol panelden PDF'lerinizi yükleyip işleyin."}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Örn: AB Yapay Zeka Yasası'nın yüksek risk tanımı nedir?"):
        if collection.count() == 0:
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            st.chat_message("assistant").write("HATA: Lütfen önce dokümanlarınızı yükleyin ve 'Dokümanları İşle ve Kaydet' butonuna basın.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Asistanınız dokümanları analiz ediyor..."):
                    response = ask_rag_assistant(prompt, gemini_client, collection, embedding_function)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.write(response)

if __name__ == "__main__":
    main()
