# -*- coding: utf-8 -*-

import streamlit as st
import google.generativeai as genai # <-- Sadece bu import eklendi

st.set_page_config(page_title="Import Test 1")
st.title("Import Test: google.generativeai")
st.write("Eğer bu yazıyı görüyorsanız, 'google.generativeai' importu sorunsuz.")

print("--- google.generativeai import denendi ---")
