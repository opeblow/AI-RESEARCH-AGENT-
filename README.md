Built by Mobolaji Opeyemi Bolatito 
A sophisticated Corrective RAG system that intelligently combines local PDF document retrieval with web search fallback to provide accurate,well-sourced answers to user queries.


## TABLE OF CONTENTS
  . Overview
  . Features
  .Architecture
  .Installation
  .Configuration
  .Usage
  .Project Structure
  .How it works
  .Contributing


## OVERVIEW
CRAG(Corrective Retrieval-Augmented Generation) is an intelligent question answering system that:

1. Retrieves relevant information from your local PDF documents.
2. Grades the quality and relevance of retrieved documents.
3. Corrects by falling back to web search when local documents are insufficient.
4. Generates accurate answers with proper source citations

This hybrid approach ensures you get the best possible answer whether the information exists in your local knowkleded base or needs to be fetched from the web.

## FEATURES
1. Smart Document Retrieval: Vector-based search through local PDF documents.
2. Quality Grading:Fallback Brave Search integration for current/missing information.
3. Sources Citation: Every answer includes traceable sources.
4. Langgraph Workflow:State machine-based processing pipeline.
5. Dual Interface:Both CLI and chainlit web UI available.
6. Chainlit Web UI:Beautiful interactive web interface with chat hstory.
6. GPT-4 Powered:Leverages OpenAI's GPT-4o-mini for generation.


## ARCHITECTURE

┌─────────────┐
│   User      │
│   Query     │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   RETRIEVE      │  ← Fetch from local PDFs
│   (Vector DB)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GRADE DOCS     │  ← Score relevance (0-1)
│  (LLM Grader)   │
└────────┬────────┘
         │
         ▼
    ┌────┴────┐
    │ Quality │
    │ Check?  │
    └─┬────┬──┘
      │    │
 <2 good chunks  ≥2 good chunks
      │    │
      ▼    ▼
┌──────────┐  ┌──────────┐
│   WEB    │  │ GENERATE │
│  SEARCH  │  │  ANSWER  │
└────┬─────┘  └────┬─────┘
     │             │
     └──────┬──────┘
            ▼
    ┌──────────────┐
    │   FINAL      │
    │   ANSWER     │
    │ + CITATIONS  │
    └──────────────┘


## INSTALLATION

---PREREQUISITES
1. PYTHON 3.8 OR HIGHER
2. PIP PACKAGE MANAGER
3. OPENAI API KEY
4. BRAVE SEARCH API KEY

---STEPS
1. Clone the repository
git clone https://github.com/opeblow/AI-RESEARCH-AGENT-.git
cd AI-RESEARCH-AGENT

2. Create a virtual environment
python -m venv venv
source venv/bin/activate #On windows:venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Set up your PDF documents
mkdir data #Place your PDF files in the data folder

## CONFIGURATION
Environment Variables 
Create .env file in the project root:
OPENAI_API_KEY=sk-your-openai-api-key-here
BRAVE_API_KEY=your-brave-api-key-here
Optional:Model Configuration
MODEL_NAME=gpt-4o-mini
TEMPERATURE=0

Getting API KEYS
OpenAIAPIKey:
1. Visit platform.openai.com
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new secret key

BRAVE SEARCH API KEY:
1. Visit brave.com/search/api
2. Sign up for API access
3. Get your API key from the dashboard

##USAGE
Run the interactive CLI:
python main.py

**EXAMPLE SESSION**
Your CRAG is ALIVE. Built by Mobolaji Opeyemi . Corrective RAG with local PDFs + Brave Search fallback
Type 'quit' to exit
Ask me anythong:What is machine learning?
Thinking.....

Retrieving from local documents...
Grading retrieved documents..
-> 3 high-quality chunks found
Generating final answer...

ANSWER
Machine learning is a subset of Artificial Intelligence that enables systems to learn and improve from experience without being explicitly programmed.It uses algorithms to identify patterns in data and make preditions or decisions based on those patterns.

SOURCES:
- [source: ml_textbook.pdf]
- [source: ai_fundamentals.pdf]
- [source: data_science_guide.pdf]

__________________________________________
BUILT by Mobolaji Opeyemi .CRAG System
__________________________________________
Ask me anything:

## PROJECT STRUCTURE
AI-REASEARCH-AGENT/
│
├── main.py                 # Entry point - CLI interface
├── chainlit_app.py         # Chainlit web UI application
├── chainlit.md             # Chainlit welcome/config file
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── .gitignore             # Git ignore rules
├── README.md              # This file
│
├── app/
│   ├── _init_.py
│   ├── agent.py           # LangGraph workflow definition
│   ├── nodes.py           # Processing nodes (retrieve, grade, search, generate)
│   ├── models.py          # Pydantic models for state management
│   ├── tools.py           # Retriever and search tools
│   ├── prompts.py         # LLM prompt templates
│   └── utils.py           # Utility functions (PDF loading, embeddings)
│
├── data/                  # Place your PDF documents here
│   ├── document1.pdf
│   ├── document2.pdf
│   └── ...
│
└── .chainlit/            # Chainlit config (auto-generated)
    └── config.toml


## HOW IT WORKS
1. Retrieval Phase: 
    . User query is embedded using OpenAI embeddings.
    . Vector similarity search retrieves top-k relevant chunks from local PDFs
    . Documents are ranked by relevance score

2. Grading Phase:
    . Each retrieved document is evaluated by an LLM grader
    . Grader assigns relevance score(0.0 -1.0) and grade (RELEVANT/IRRELEVANT)
    . One highly-quality chunks(score > 0.7) are considered

3. Decision Phase:
    . If >=2 high-quality chunks found -> proceed to generation
    .if <2 high-quality chunks -> trigger web search fallback


4. Web Search Phase(IF TRIGGERED)
    . Query sent to Brave Search API
    . Top 5 web results retrieved
    . Results added to document pool

5. Generation Phase:
     . All relevant documents combined into context
     . GPT-4 generates comprehensive anser
     . Citations extracted from document metadata





## CONTRIBUTING
Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'ADD SOME AMAZING FEATURES')
4. Open a pull request



## ACKNOWLEDGEMENTS
  - Built with langchain and langGraph
  - Powered by OpenAIGPT-4
  - Web search via BraveSearchAPI



## CONTACT
  - Email: opeblow2021gmail.com

