# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (SON VE HATASIZ SÜRÜM - Final SyntaxError Fix 3)
# =================================================================================

import streamlit as st
import os
import glob
import tempfile
import textwrap
import traceback # Import traceback at the top

# RAG Bileşenleri
# ===========================================
# IMPORT DEBUGGING BLOĞU (Final Syntax fix included)
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
        print(f"--- APIError başarıyla atandı: {APIError} ---")

except ImportError as e:
    print(f"!!! google.generativeai import edilemedi:")
    print(repr(e))
    st.
