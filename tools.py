"""
Tool handlers — replace the placeholder strings with your actual content.

Each function returns compact, labeled plain text. Models parse labeled formats
(Role:, Period:, Highlights:) reliably and they cost fewer tokens than prose.
"""


def get_about() -> str:
    return """\
Name: Alex Chen
Current role: Senior AI Engineer at TechCorp
Location: Singapore
Positioning: Applied AI engineer specialising in LLM systems, RAG pipelines, \
and agentic workflows. Ph.D. in Computer Science (NUS, 2022).
Domains: Agentic AI · GenAI / LLMs · Computer Vision · NLP · Data Engineering
Languages: English, Mandarin
Open to: Consulting engagements, speaking, research collaboration
"""


def get_experience() -> str:
    return """\
--- Work ---
Company: TechCorp
Role: Senior AI Engineer
Period: Jan 2023 – present
Location: Singapore (hybrid)
Highlights:
  - Led end-to-end design of a multi-agent document analysis platform (LangGraph, GPT-4o)
  - Built RAG pipeline over 500k legal documents; reduced lawyer review time by 60%
  - Introduced LLM-as-judge evaluation gate that blocked 3 regressions in CI

Company: DataLab Consulting
Role: Machine Learning Engineer
Period: Jul 2020 – Dec 2022
Location: Singapore
Highlights:
  - Delivered computer vision defect detection for semiconductor client; 98.5% precision
  - Productionised time-series forecasting model serving 40M predictions/day on AWS SageMaker

--- Education ---
Degree: Ph.D. Computer Science
Institution: National University of Singapore
Period: 2018 – 2022
Thesis: Efficient Retrieval-Augmented Generation for Long-Document QA

Degree: B.Eng. Electrical Engineering (First Class Honours)
Institution: Nanyang Technological University
Period: 2014 – 2018
"""


def get_projects() -> str:
    return """\
--- Project: Legal Document AI Platform ---
Client: Global law firm (confidential) · via TechCorp
Period: 2023 – 2024
Problem: Lawyers spent 4+ hours per matter reviewing contracts manually.
Approach: Multi-agent pipeline — a routing agent, a clause-extraction agent, \
and a risk-scoring agent — over a RAG index of 500k documents (pgvector, \
BM25 hybrid retrieval).
Stack: Python · FastAPI · LangGraph · GPT-4o · pgvector · AWS ECS
Impact: Reduced review time by 60%, flagged clause anomalies with 91% precision.
Metrics: 91% precision on clause anomaly detection · 60% review-time reduction

--- Project: Semiconductor Defect Detection ---
Client: Semiconductor manufacturer · Singapore
Period: 2021 – 2022
Problem: Manual visual inspection of wafers missed 5–8% of defects.
Approach: Fine-tuned EfficientNet-B4 on 120k annotated wafer images, \
deployed as a FastAPI microservice with a React review dashboard.
Stack: PyTorch · EfficientNet · FastAPI · React · AWS SageMaker
Impact: Defect miss-rate fell to <0.3%.
Metrics: 98.5% precision · <0.3% miss-rate
"""


def get_publications() -> str:
    return """\
--- Journal Papers ---
Title: Efficient RAG for Long-Document Question Answering
Venue: ACL 2023
Authors: Alex Chen, Wei Liu, Priya Sharma
Abstract: Proposes a two-stage retrieval approach (BM25 coarse + cross-encoder \
reranking) that improves answer F1 by 8 points over DPR on long legal documents.
Citations: 47

--- Conference Papers ---
Title: Adaptive Chunking Strategies for Retrieval-Augmented Generation
Venue: EMNLP 2022
Authors: Alex Chen, Raj Patel
Abstract: Empirical study of chunk-size and overlap trade-offs across six RAG benchmarks.
Citations: 31

--- Research Impact ---
Google Scholar h-index: 5
Total citations: 78
"""
