# -*- coding: utf-8 -*-

import streamlit as st
import google.generativeai as genai
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings # <-- langchain_google_genai importu eklendi

st.set_page_config(page_title="Import Test 3")
st.title("Import Test: langchain_google_genai")
st.write("Eğer bu yazıyı görüyorsanız, 'langchain_google_genai' importu da sorunsuz.")
st.write("(Önceki google.generativeai ve chromadb importları da çalışmıştı.)")

print("--- langchain_google_genai import denendi ---")
