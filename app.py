# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (SON VE HATASIZ SÜRÜM - Import Debugging)
# =================================================================================

import streamlit as st
import os
import glob
import tempfile
import textwrap

# RAG Bileşenleri
# ===========================================
# IMPORT DEBUGGING BLOĞU
try:
    import google.generativeai
    print("--- google.generativeai başarıyla import edildi ---")
    print(dir(google.generativeai)) # Modülün içindekileri yazdır
    genai = google.generativeai # genai adını manuel olarak atayalım
    # APIError'ı dinamik olarak bulmaya çalışalım (varsa)
    # Önce .errors altında arayalım (standart konum)
    APIError = getattr(genai.errors, 'APIError', None)
    if APIError is None:
        # Eğer orada yoksa, doğrudan genai altında arayalım (eski sürümler?)
        APIError = getattr(genai, 'APIError', None)

    if APIError is None:
        print("!!! APIError sınıfı genai veya genai.errors altında bulunamadı !!!")
        # Geçici olarak genel Exception kullanalım ki kod çalışsın
        APIError = Exception
    else:
        print(f"--- APIError başarıyla bulundu: {APIError} ---")

except ImportError as e:
    print(f"!!! google.generativeai import edilemedi: {e
