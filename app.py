# -*- coding: utf-8 -*-

# =================================================================================
# 5. ADIM: STREAMLIT WEB UYGULAMASI (SON VE HATASIZ SÜRÜM - Indentation Fix)
# =================================================================================

import streamlit as st
import os
import glob
import tempfile
import textwrap
import traceback # Import traceback at the top

# RAG Bileşenleri
# ===========================================
# IMPORT DEBUGGING BLOĞU (Indentation Fix included)
try:
    import google.generativeai
    print("--- google.generativeai başarıyla import edildi ---")
    genai = google.generativeai

    APIError_class = None
    # Check under genai.errors first
    if hasattr(genai, 'errors') and hasattr(genai.errors, 'APIError'):
        APIError_class = genai.errors.APIError
        print(f"--- APIError genai.errors altından bulundu: {APIError_class} ---")
    # If not found there, check directly under genai
    elif hasattr(genai, 'APIError'):
         APIError_class = genai.APIError
         print(f"--- APIError genai altından bulundu: {APIError_class} ---")

    # Now, assign the final class or fallback
    # ===========================================
    # INDENTATION FIX HERE
    if APIError_class is None:
        print("!!! APIError sınıfı genai veya genai.errors altında bulunamadı !!!") # Indented
        APIError = Exception # Fallback                                          # Indented
    else:
        APIError = APIError_class # Indented
        print(f"--- APIError başarıyla atandı: {APIError} ---")                   # Indented
    # ===========================================

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
    print(f"!!! Import sırasında beklenmedik hata:")
    print(repr(e))
    st.error(f"Kritik Başlangıç Hatası. Detay: {repr(e)}")
    st.stop()
# ===========================================

from chromadb import Client
