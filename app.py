import streamlit as st

st.set_page_config(page_title="Super Basic Test")
st.title("Eğer bunu görüyorsan, Streamlit çalışıyor!")

print("--- Minimal Test Script Çalıştı ---") # Loglara yazacak
import google.generativeai as genai # <-- Sadece bunu ekle

st.set_page_config(page_title="Import Test 1")
st.title("Import Test: google.generativeai")
st.write("Eğer bunu görüyorsan, 'google.generativeai' importu sorunsuz.")

print("--- google.generativeai import denendi ---")

