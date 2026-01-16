# 🔎 Semantic CV Analyzer

**Semantic CV Analyzer** is an AI-powered tool designed to bridge the gap between candidate resumes and job descriptions using advanced Natural Language Processing (NLP).

Unlike traditional keyword-matching ATS systems, this tool utilizes **Google's Gemini 2.5 LLM** to perform semantic analysis, understanding the *context* of skills and experience rather than just matching words.

---

## 🚀 Key Features

* **Context-Aware Analysis:** Uses Generative AI to understand the nuance of job requirements.
* **Multi-Dimensional Scoring:** breaks down the evaluation into:
    * 🛠 **Technical Match:** Hard skills and stack alignment.
    * 📅 **Experience Match:** Seniority and domain relevance.
    * 🧠 **Soft Skills:** Communication and leadership indicators.
* **PDF Parsing:** Native Python-based PDF text extraction.
* **ATS Optimization:** Identifies critical missing keywords that might block a CV in automated systems.

## 🛠 Tech Stack

* **Python 3.9+**
* **Streamlit:** For the interactive web interface.
* **Google Generative AI (Gemini 2.5):** For semantic reasoning and scoring.
* **PyPDF2:** For document processing.

## ⚙️ Installation & Usage

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/nezirayaz/semantic-cv-analyzer.git](https://github.com/nezirayaz/semantic-cv-analyzer.git)
    cd semantic-cv-analyzer
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Key:**
    Create a `.streamlit/secrets.toml` file in the project root:
    ```toml
    google_api_key = "YOUR_GOOGLE_API_KEY"
    ```

4.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

## 👨‍💻 Author

**Nezir Ayaz**
* [LinkedIn](https://www.linkedin.com/in/nezirayaz/)
* [GitHub](https://github.com/nezirayaz/)

## 📄 License

This project is licensed under the MIT License.