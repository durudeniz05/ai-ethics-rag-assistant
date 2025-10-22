# 🤖 Yapay Zeka Etiği ve Uyum RAG Asistanı

Bu proje, Akbank GenAI Bootcamp kapsamında geliştirilen, **Retrieval-Augmented Generation (RAG)** temelli bir yapay zeka destekli sohbet robotudur.

## 1. Projenin Amacı

Bu RAG asistanının temel amacı, kullanıcıların Türkiye ve uluslararası alandaki (AB, OECD) Yapay Zeka (YZ) etik kuralları, ulusal stratejiler ve yasal uyum konularındaki **PDF dokümanlarına dayalı** doğru ve güvenilir cevaplar almasını sağlamaktır. Kullanıcılar, Streamlit web arayüzü üzerinden diledikleri dokümanları yükleyebilir ve bot, ürettiği her cevabı ilgili resmi kaynağa atıfta bulunarak destekler.

## 2. Veri Seti Hakkında Bilgi

Proje, Türkiye'deki ulusal stratejiler, etik rehberler, AB'nin Yapay Zeka Yasası ve OECD'nin uluslararası YZ İlkeleri dahil olmak üzere kapsamlı bir veri seti üzerine kurulmuştur.

| Dosya Adı | İçerik Özeti |
| :--- | :--- |
| `REGULATION (EU) 2024/1689... (Artificial Intelligence Act)` | Avrupa Parlamentosu ve Konseyi'nin YZ'ye ilişkin uyumlaştırılmış kurallarını belirleyen ve **AB Yapay Zeka Yasası (AI Act)** olarak bilinen düzenlemedir. YZ sistemleri için risk temelli yaklaşımı içerir. |
| `What are the OECD Principles on AI?.pdf` | OECD tarafından belirlenen ve YZ'nin sorumlu inovasyonunu teşvik eden, uluslararası kabul görmüş temel etik ve yönetim ilkeleridir. |
| `TR-UlusalYZStratejisi2021-2025.pdf` | Türkiye Cumhuriyeti'nin 2021-2025 dönemine ait Yapay Zeka alanındaki resmi stratejilerini ve hedeflerini içerir. |
| `UYZ_Rehberi_v03_TR.pdf` | Yapay Zeka teknolojilerinin geliştirilmesi ve kullanımı için detaylı etik rehberlik sağlar. |
| `Yapay-Zeka-Alaninda-Kisisel-Verilerin-Korunmasina-Dair-Tavsiyeler.pdf` | YZ sistemlerinde Kişisel Verilerin Korunması Kanunu (KVKK) uyumu ve uygulama tavsiyeleri üzerine odaklanır. |

## 3. Kodunuzun Çalışma Kılavuzu (Lokal Kurulum)

Bu projeyi kendi yerel ortamınızda çalıştırmak için aşağıdaki adımları takip edin:

1.  **Sanal Ortam Kurulumu:** Python'da izole bir ortam oluşturun.
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate     # Windows
    ```

2.  **Gereksinimleri Yükleme:** Proje bağımlılıklarını `requirements.txt` dosyasından yükleyin.
    ```bash
    pip install -r requirements.txt
    ```
    *(Not: `requirements.txt` dosyasını `app.py` dosyanızdaki tüm kütüphanelerle oluşturduğunuzdan emin olun: `pip freeze > requirements.txt`)*

3.  **API Anahtarını Ayarlama:** Streamlit uygulamasının çalışması için Gemini API anahtarınızı (veya `secrets.toml` dosyanızı) ayarlayın.
    * **Lokal Çalıştırma:** `os.environ` kullanarak veya `.streamlit/secrets.toml` dosyasını oluşturarak anahtarınızı tanımlayın. (Örn: `export GEMINI_API_KEY="AIzaSy..."`)

4.  **Uygulamayı Başlatma:** Projenin ana dosyası olan `app.py` dosyasını Streamlit ile başlatın.
    ```bash
    streamlit run app.py
    ```

## 4. Çözüm Mimarisi

Proje, LangChain kütüphanesi ve Google'ın GenAI teknolojileri kullanılarak modern bir RAG mimarisi üzerine inşa edilmiştir.

| Bileşen | Kullanılan Teknoloji | Rol |
| :--- | :--- | :--- |
| **Arayüz** | `Streamlit` | Web arayüzü ve kullanıcı etkileşimi için kullanılır. |
| **RAG Çatısı** | `LangChain` | RAG pipeline'ının orkestrasyonunu sağlar. |
| **Metin Parçalama** | `RecursiveCharacterTextSplitter` | PDF'leri uygun 'chunk'lara ayırır. |
| **Gömme (Embedding) Modeli** | `GoogleGenerativeAIEmbeddings` (`models/text-embedding-004`) | Metin parçalarını vektörlere dönüştürür. |
| **Vektör Veritabanı** | `ChromaDB` | Vektörleri depolayarak hızlıca bağlamsal arama yapılmasını sağlar. |
| **LLM (Generation Model)** | `Gemini-2.5-Flash` (Google GenAI) | Çekilen bağlamı kullanarak nihai cevabı üretir. |

**Çözüm Mimarisi Akışı:** İndeksleme (PDF -> Chunking -> Vektör) ve Sorgulama (Soru -> Vektör Arama -> Context -> LLM ile Cevap Üretimi) adımlarından oluşur.

## 5. Web Arayüzü & Product Kılavuzu

Projenin canlı olarak çalışan web arayüzü ve kullanım adımları aşağıdadır.

**Canlı Uygulama (Deploy) Linki:**
https://ai-ethics-rag-assistant-mju5fysvtxyslhqjhplmrk.streamlit.app/

### Çalışma Akışı ve Test Adımları

1.  **Doküman Yükleme:** Arayüzün sol menüsünde yer alan **"1. Doküman Yükleme (PDF)"** alanından, test etmek istediğiniz tüm PDF dosyalarını yükleyin.
2.  **İşle ve Kaydet:** Yükleme tamamlandıktan sonra, **"Dokümanları İşle ve Kaydet"** butonuna basarak RAG pipeline'ının dokümanları parçalayıp ChromaDB'ye kaydetmesini bekleyin. İşlem tamamlandığında menüde **"Kayıtlı Parça: [Sayı]"** bilgisini göreceksiniz.
3.  **Sorgulama:** Sohbet alanına etik, uyum veya strateji konularında bir soru yazın (Örn: "AB Yapay Zeka Yasası'nın risk seviyeleri nelerdir?" veya "OECD'nin YZ İlkeleri nelerdir?").
4.  **Kabiliyet Testi:** Botun cevabının, yalnızca yüklenen dokümanlardaki bilgilere dayanıp dayanmadığını ve cevap sonunda kaynak (source) bilgisini belirtip belirtmediğini kontrol edin.

## 6. Elde Edilen Sonuçlar

* **Başarılı RAG Uygulaması:** Proje, yüklenen dokümanlara özgü, harici internet bilgisine dayanmayan doğru cevaplar üretebilme yeteneğini göstermiştir.
* **Kanıtlanabilir Kaynak Atfı:** Üretilen her cevap, RAG mekanizması sayesinde hangi dokümandan ve hangi sayfadan geldiğini belirten kaynak bilgileriyle (metadatalarla) desteklenmiştir.
* **Stabil Dağıtım:** Uygulama, Streamlit üzerinde başarılı bir şekilde dağıtılmış (deploy edilmiş) ve canlı olarak test edilebilir durumdadır.
