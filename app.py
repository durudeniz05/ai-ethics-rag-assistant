# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (SON VE HATASIZ SÜRÜM - Colon Fix)
# =================================================================================

import streamlit as st
import os
import glob
import tempfile
import textwrap
import traceback # Import traceback at the top

# RAG Bileşenleri
# ===========================================
# IMPORT DEBUGGING BLOĞU
try:
    import google.generativeai
    print("--- google.generativeai başarıyla import edildi ---")
    # print(dir(google.generativeai)) # Logları temiz tutmak için bunu yorumlayalım
    genai = google.generativeai

    # APIError'ı dinamik olarak bulmaya çalışalım (varsa)
    APIError_class = None
    if hasattr(genai, 'errors') and hasattr(genai.errors, 'APIError'):
        APIError_class = genai.errors.APIError
        print(f"--- APIError genai.errors altından bulundu: {APIError_class} ---")
    elif hasattr(genai, 'APIError'):
         APIError_class = genai.APIError
         print(f"--- APIError genai altından bulundu: {APIError_class} ---")

    if APIError_class is None:
        print("!!! APIError sınıfı genai veya genai.errors altında bulunamadı !!!")
        APIError = Exception # Fallback
    else:
        APIError = APIError_class

except ImportError as e:
    print(f"!!! google.generativeai import edilemedi:")
    print(repr(e))
    st.error(f"Kritik Import Hatası: google.generativeai yüklenemedi. Detay: {repr(e)}")
    st.stop()
except AttributeError as e:
    print(f"!!! genai.errors bulunamadı veya APIError aranırken hata: {e} !!!")
    APIError = Exception
    print("--- APIError için genel Exception kullanılacak ---")
except Exception as e:
    print(f"!!! Import sırasında beklenmedik hata: {e}
