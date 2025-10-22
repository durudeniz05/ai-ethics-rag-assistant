# -*- coding: utf-8 -*-

import streamlit as st
import google.generativeai as genai
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter # <-- langchain_text_splitters importunu ekle

st.set_page_config(page_title="Import Test 4")
st.title("Import Test: langchain_text_splitters")
st.write("Eğer bu yazıyı görüyorsanız, 'langchain_text_splitters' importu da sorunsuz.")
st.write("(Önceki google.generativeai, chromadb ve langchain_google_genai importları da çalışmıştı.)")

print("--- langchain_text_splitters import denendi ---")
