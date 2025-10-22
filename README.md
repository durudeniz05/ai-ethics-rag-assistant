# ai-ethics-rag-assistant
# 🤖 AI Ethics & Compliance RAG Assistant (Yapay Zeka Etiği ve Uyum RAG Asistanı)

## Akbank GenAI Bootcamp Projesi

Bu proje, Retrieval Augmented Generation (RAG) mimarisini kullanarak Yapay Zeka Etiği ve Uyum dokümanlarına dayalı güvenilir ve kaynak gösteren bir chatbot geliştirmeyi amaçlamaktadır. Proje, web arayüzü üzerinden sunulmaktadır.

---

## 1. Projenin Amacı

Bu asistan, ulusal (Türkiye) ve uluslararası (AB, OECD) ölçekteki yapay zeka etik ilkeleri ve yasal düzenlemeleri üzerine bir bilgi tabanı oluşturur. Amacı, kullanıcılara (AI geliştiricileri/uyum uzmanları) yasal metinlere dayalı, güvenilir cevaplar sunmak ve ürünlerinin etik/yasal uyum risklerini hızlıca değerlendirmelerine yardımcı olmaktır.

## 2. Veri Seti Hakkında Bilgi

Veri seti, yasal uyum ve etik rehberlik sağlayan resmi otoritelerin yayımladığı metinlerden oluşmaktadır.

* **İçerik:** T.C. Dijital Dönüşüm Ofisi Ulusal Yapay Zeka Stratejisi, AB Yapay Zeka Yasası (AI Act) özetleri/kılavuzları ve OECD Yapay Zeka Etiği İlkeleri gibi hukuki ve stratejik PDF dokümanlarıdır.
* **Hazırlama Metodolojisi:** Dokümanlar manuel olarak toplanmış, `PyPDFLoader` ile metinleri çıkarılmış ve `RecursiveCharacterTextSplitter` ile parçalara (chunk) ayrılmıştır. Bu parçalar, LLM'in işleyeceği bağlamı oluşturur.

## 3. Kullanılan Yöntemler (Çözüm Mimarisi)

RAG sistemi, Colab ortamında yaşanan framework/API çakışmalarını aşmak için **LangChain ve Google API'lerinin manuel entegrasyonu** ile kurulmuştur.

| Bileşen | Seçim | Açıklama |
| :--- | :--- | :--- |
| **RAG Pipeline Framework** | Manuel Entegrasyon (Python) | LangChain ve Haystack yerine, Google API'leri ve Chroma DB'nin temel kütüphaneleri kullanılarak özel bir RAG akışı oluşturulmuştur. |
| **Generation Model (LLM)** | Gemini API (`gemini-2.5-flash`)  | Soru ve bağlamı analiz ederek nihai, kaynak gösteren cevabı üretmek için kullanılmıştır. |
| **Embedding Model** | ]Google Generative AI Embeddings  | Metin parçalarını ve kullanıcı sorgusunu sayısal vektörlere çevirmek için kullanılmıştır. |
| **Vector Database** | Chroma DB  | Vektörleri depolamak ve sorguya en alakalı parçaları hızlıca geri getirmek (Retrieval) için kullanılmıştır. |
| **Web Arayüzü** | Streamlit | Chatbot'un interaktif bir arayüz üzerinden sunulması için kullanılmıştır. |

## 4. Elde Edilen Sonuçlar Özet

Geliştirilen RAG Asistanı:

* **Doğruluk ve Güvenilirlik:** Yalnızca yüklenen dokümanlara odaklanarak yüksek doğrulukta yanıtlar üretmiş ve kendi bilgisini eklememiştir.
* **Kaynak Gösterme:** Cevapların sonunda, bilginin alındığı PDF dosyasının adını (`[Kaynak: Dosya Adı]`) belirterek şeffaflık sağlamıştır.
* **Kullanılabilirlik:** Streamlit arayüzü sayesinde, kullanıcılar kendi yeni PDF dokümanlarını yükleyip anında Vektör Veritabanı'na ekleyebilmekte ve uyum analizine başlayabilmektedir.

## 5. Web Arayüzü & Deploy Linki

Proje, **Streamlit Cloud** platformuna deploy edilmiştir. Deploy linkiniz mutlaka paylaşılmalıdır.

* **Kullanım Kılavuzu:** Uygulama açıldığında, kullanıcılar sol paneldeki yükleme alanını kullanarak kendi PDF'lerini yükleyebilir ve **"Dokümanları İşle ve Kaydet"** butonuna basarak bilgi tabanını anlık olarak güncelleyebilir. Ardından, ana sohbet kutusuna sorularını yazabilirler.

**WEB UYGULAMA LİNKİ:**
https://ai-ethics-rag-assistant-mju5fysvtxyslhqjhplmrk.streamlit.app/

---

**PROJE ÇALIŞMA KILAVUZU**

Bu projeyi yerel olarak çalıştırmak için, aynı klasörde bulunan `requirements.txt` dosyasındaki kütüphaneleri sanal ortamda kurmalı ve `.streamlit/secrets.toml` dosyasında `GEMINI_API_KEY`'i tanımlamalısınız.

```bash
# Gerekli kütüphaneleri kurmak için
pip install -r requirements.txt

# Streamlit uygulamasını başlatmak için
streamlit run app.py
