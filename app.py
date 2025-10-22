# -*- coding: utf-8 -*-

import streamlit as st
import google.generativeai as genai
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader # <-- langchain_community importunu ekle

st.set_page_config(page_title="Import Test 5")
st.title("Import Test: langchain_community (PyPDFLoader)")
st.write("Eğer bu yazıyı görüyorsanız, 'langchain_community' (PyPDFLoader) importu da sorunsuz.")
st.write("(Önceki tüm importlar da çalışmıştı.)")

print("--- langchain_community.document_loaders import denendi ---")
