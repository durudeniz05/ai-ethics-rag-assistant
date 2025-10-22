# -*- coding: utf-8 -*-

import streamlit as st
import google.generativeai as genai
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import traceback

print("--- DEBUG: Tüm importlar tamamlandı ---")

# --- 1. API Anahtarını Oku ---
GEMINI_API_KEY = None # Başlangıç değeri
try:
    print("--- DEBUG: Secrets okunuyor... ---")
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    print("--- DEBUG: Secrets okundu. ---")
except KeyError:
    print("!!! Secrets içinde GEMINI_API_KEY bulunamadı! ---")
    st.error("HATA: Streamlit Secrets'ta 'GEMINI_API_KEY' bulunamadı.")
    st.stop()
except Exception as e:
    print(f"!!! Secrets okunurken beklenmedik hata: {e} !!!")
    st.error(f"Secrets okunurken HATA: {e}")
    st.stop()

# --- 2. Minimal Setup Fonksiyonu (Cache Yok, İçi Boş) ---
def setup_rag_components_minimal():
    """Sadece çağrılıp çağrılmadığını test et."""
    print("--- DEBUG: setup_rag_components_minimal BAŞLADI ---")
    # İçinde hiçbir şey yapma, sadece None döndür
    print("--- DEBUG: setup_rag_components_minimal TAMAMLANDI ---")
    return None, None, None, None # llm, embedding, splitter, collection

# --- 3. Main Fonksiyonu ---
def main():
    print("--- DEBUG: main() BAŞLADI ---")
    st.set_page_config(page_title="Setup Call Test")
    st.title("Setup Fonksiyon Çağrı Testi")
    st.write("Eğer bu yazıyı görüyorsanız, Secrets okundu ve minimal setup fonksiyonu çağrıldı.")

    # Minimal setup fonksiyonunu çağırmayı dene
    try:
        print("--- DEBUG: setup_rag_components_minimal çağrılıyor... ---")
        llm, embedding_function, text_splitter, collection = setup_rag_components_minimal()
        print("--- DEBUG: setup_rag_components_minimal'dan dönüldü ---")
        st.success("Minimal setup fonksiyonu başarıyla çağrıldı ve geri döndü.")
        st.info(f"Dönen Değerler (Beklenen: None): {llm}, {embedding_function}, {text_splitter}, {collection}")
    except Exception as e:
        print(f"!!! setup_rag_components_minimal çağrılırken HATA: {e} !!!")
        st.error(f"Minimal setup fonksiyonu çağrılırken hata oluştu: {e}")
        st.stop()

    st.info("Sonraki adım: setup fonksiyonunun içini doldurmak.")

if __name__ == "__main__":
    main()
