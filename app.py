"""
Semantic CV Analyzer
AI-Powered Resume Analysis & Scoring Tool

This application leverages Large Language Models (LLM) to perform semantic analysis
between candidate resumes (CVs) and job descriptions. Unlike traditional keyword
matching, it uses Generative AI to understand context, seniority, and soft skills.

Key Capabilities:
    - Semantic Text Extraction (PDF)
    - Context-Aware RAG (Retrieval-Augmented Generation) Analysis
    - Multi-dimensional Scoring (Technical, Experience, Soft Skills)
    - JSON-Structured Output Parsing

Author: Nezir Ayaz
Version: 1.0.0
License: MIT
"""

import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import PyPDF2
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

try:
    import google.generativeai as genai
except ImportError:
    st.error("Required package 'google-generativeai' is not installed.")
    st.stop()


# ============================================================================
# Configuration and Constants
# ============================================================================

class ScoreThreshold(Enum):
    """Thresholds for visual score indicators."""
    EXCELLENT = 80
    MODERATE = 60
    WEAK = 0


class AppConfig:
    """Application configuration."""
    PAGE_TITLE = "Semantic CV Analyzer"
    PAGE_ICON = "🔎"
    LAYOUT = "wide"
    # Using the latest efficient model
    MODEL_NAME = "gemini-2.5-flash" 
    
    # UI Layout Config
    JOB_DESC_HEIGHT = 300
    
    # Logging Config
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class AnalysisResult:
    """Data transfer object for analysis results."""
    technical_score: int
    experience_score: int
    soft_skill_score: int
    overall_average: int
    missing_keywords: List[str]
    candidate_summary: str
    interview_question: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        return cls(
            technical_score=int(data.get('technical_score', 0)),
            experience_score=int(data.get('experience_score', 0)),
            soft_skill_score=int(data.get('soft_skill_score', 0)),
            overall_average=int(data.get('overall_average', 0)),
            missing_keywords=data.get('missing_keywords', []),
            candidate_summary=data.get('candidate_summary', 'N/A'),
            interview_question=data.get('interview_question', 'N/A')
        )


# ============================================================================
# Logging Setup
# ============================================================================

logging.basicConfig(level=AppConfig.LOG_LEVEL, format=AppConfig.LOG_FORMAT)
logger = logging.getLogger("SemanticAnalyzer")


# ============================================================================
# Core Logic Classes
# ============================================================================

class PDFProcessor:
    """Handles PDF file operations."""
    
    @staticmethod
    def extract_text(uploaded_file: UploadedFile) -> Optional[str]:
        """Parses text from PDF file stream."""
        try:
            reader = PyPDF2.PdfReader(uploaded_file)
            text = " ".join(page.extract_text() for page in reader.pages if page.extract_text())
            
            if not text:
                st.error("Could not extract text. PDF might be image-based.")
                return None
                
            return text
        except Exception as e:
            logger.error(f"PDF Processing Error: {e}")
            st.error(f"Error reading PDF: {e}")
            return None


class AIAnalyzer:
    """Engine for LLM-based analysis."""
    
    def __init__(self, api_key: str):
        self.model = self._configure_model(api_key)
    
    def _configure_model(self, api_key: str):
        try:
            genai.configure(api_key=api_key)
            return genai.GenerativeModel(
                AppConfig.MODEL_NAME,
                generation_config=genai.GenerationConfig(response_mime_type="application/json")
            )
        except Exception as e:
            st.error(f"Model Configuration Error: {e}")
            return None
    
    def analyze(self, job_desc: str, cv_text: str) -> Optional[AnalysisResult]:
        if not self.model: return None
        
        prompt = f"""
        ROLE: Senior Technical Recruiter & AI Engineer.
        TASK: Analyze the Candidate CV against the Job Description.
        
        JOB DESCRIPTION:
        {job_desc}
        
        CANDIDATE CV:
        {cv_text}
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "technical_score": <0-100>,
            "experience_score": <0-100>,
            "soft_skill_score": <0-100>,
            "overall_average": <0-100>,
            "missing_keywords": ["list", "of", "missing", "tech", "keywords"],
            "candidate_summary": "Technical summary of the candidate.",
            "interview_question": "One hard technical interview question."
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            data = json.loads(response.text)
            return AnalysisResult.from_dict(data)
        except Exception as e:
            logger.error(f"AI Analysis Error: {e}")
            st.error("Analysis failed. Please try again.")
            return None


# ============================================================================
# UI Components
# ============================================================================

class UIRenderer:
    """Handles Streamlit UI rendering."""
    
    @staticmethod
    def render_header():
        st.title("🔎 Semantic CV Analyzer")
        st.markdown("")
        st.markdown("---")
    
    @staticmethod
    def render_inputs():
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📋 Job Description")
            jd = st.text_area("Paste JD here:", height=300)
        with col2:
            st.subheader("📄 Candidate CV")
            cv = st.file_uploader("Upload PDF", type=["pdf"])
        return jd, cv

    @staticmethod
    def render_results(res: AnalysisResult):
        st.markdown("---")
        st.subheader(f"Overall Match: {res.overall_average}%")
        st.progress(res.overall_average / 100)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("🛠 Technical", f"{res.technical_score}%")
        c2.metric("📅 Experience", f"{res.experience_score}%")
        c3.metric("🧠 Soft Skills", f"{res.soft_skill_score}%")
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.error("🚨 Missing Keywords")
            for k in res.missing_keywords: st.write(f"- {k}")
        with col2:
            st.info("💡 Analysis Summary")
            st.write(res.candidate_summary)
            st.write(f"**Question:** *{res.interview_question}*")


# ============================================================================
# Main App Logic
# ============================================================================

def main():
    st.set_page_config(page_title=AppConfig.PAGE_TITLE, page_icon=AppConfig.PAGE_ICON, layout=AppConfig.LAYOUT)
    
    # Secure API Key Retrieval
    api_key = None
    if hasattr(st, 'secrets') and 'google_api_key' in st.secrets:
        api_key = st.secrets['google_api_key']
    else:
        import os
        api_key = os.getenv('GOOGLE_API_KEY')
        
    if not api_key:
        st.warning("⚠️ API Key missing. Please configure secrets.toml")
        st.stop()
        
    app_ui = UIRenderer()
    app_ui.render_header()
    jd, cv = app_ui.render_inputs()
    
    if st.button("Run Semantic Analysis 🚀", type="primary"):
        if jd and cv:
            with st.spinner("Analyzing semantics..."):
                processor = PDFProcessor()
                text = processor.extract_text(cv)
                if text:
                    analyzer = AIAnalyzer(api_key)
                    result = analyzer.analyze(jd, text)
                    if result:
                        app_ui.render_results(result)
        else:
            st.warning("Please provide both Job Description and CV.")

if __name__ == "__main__":
    main()