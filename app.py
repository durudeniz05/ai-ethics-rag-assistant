# -*- coding: utf-8 -*-

import streamlit as st
import google.generativeai as genai
import chromadb # <-- chromadb importu eklendi

st.set_page_config(page_title="Import Test 2")
st.title("Import Test: chromadb")
st.write("Eğer bu yazıyı görüyorsanız, 'chromadb' importu da sorunsuz.")
st.write("(Önceki google.generativeai importu da çalışmıştı.)")

print("--- chromadb import denendi ---")
