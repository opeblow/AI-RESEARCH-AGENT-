# CRAG – Corrective Retrieval-Augmented Generation System

*Built from scratch • 100% local documents + web fallback • Self-correcting • Production-grade*

 
Asks “Who won the 2025 World Series?” → sees local PDFs are irrelevant → automatically searches the web → answers with citations

A fully functional, senior-level Corrective RAG implementation that:
- Ingests PDFs, DOCX, HTML, TXT via *Unstructured.io*
- Embeds with *all-MiniLM-L6-v2* → stores in *FAISS*
- Uses *LangGraph* for stateful, conditional routing
- Grades retrieval quality in real time
- Falls back to *Brave Search* when local knowledge is insufficient
- Cites every claim
- Signs every answer with *your name*

Built by MOBOLAJI OPEYEMI BOLATITO OBINNA • 2025

---

### Why This Project Stands Out (Interview Talking Points)

| Feature                          | Junior RAG                | This CRAG (You)                                   |
|----------------------------------|---------------------------|----------------------------------------------------|
| Document ingestion               | PyPDF2 only             | Unstructured.io → handles tables, headers, footers |
| Chunking                         | Fixed size                | Recursive with overlap → preserves context        |
| Retrieval                        | Blind top-k               | Grades relevance → self-aware                      |
| Web fallback                     | Never                     | Brave Search when <2 high-quality chunks           |
| Architecture                     | Single chain              | LangGraph state machine → conditional edges        |
| Error handling                   | None                      | Retries on LLM + web calls                         |
| Branding                         | “Powered by GPT”          | Built by MOBOLAJI OPEYEMI BOLATITO OBINNA               |
| Deployable                       | No                        | One requirements.txt → runs anywhere             |

---

### Live Demo

```text
Ask me anything: What does the EU AI Act say about foundation models?

→ Found 9 high-quality chunks → enough local info
→ Answer cites EU_AI_Act_2024.pdf with page references

Ask me anything: Who won Miss Universe 2025?

→ Found 0 relevant chunks → going to web search
→ Answer cites missuniverse.com + Wikipedia

---
Built by MOBOLAJI OPEYEMI BOLATITO OBINNA• CRAG System (Corrective Retrieval-Augmented Generation)


crag-project/
├── main.py                  # Chat interface
├── data/                    # ← Drop your PDFs/DOCX here
├── vectorstore/             # Auto-created FAISS index
├── .env                     # Your keys (never commit!)
└── app/
    ├── agent.py             # LangGraph orchestration
    ├── nodes.py             # Retrieve → Grade → Decide → Web → Generate
    ├── tools.py             # FAISS retriever + Brave Search
    ├── utils.py             # Unstructured loading + chunking
    ├── models.py            # Pydantic + TypedDict schemas
    ├── prompts.py           # Secure, injection-proof prompts
    └── _init_.py

git clone https://github.com/OPEBLOW/CRAG.git
cd CRAG

python -m venv myenv
source myenv/bin/activate    # Windows: myenv\Scripts\activate

pip install -r requirements.txt

OPENAI_API_KEY=sk-...
BRAVE_API_KEY=bsa_XXXXXXXXXXXXXXXXXXXXXXXx

python main.py #To run the code

Tech Stack;
Purpose                                Libray/Tool

|__Orchestration                      |__langgraph
|__LLM                                |__gpt-4o
|__Embeddings                         |__all-MiniLM-L6-v2
|__Vector DB                          |__FAISS(CPU)
|__Document Parsing                   |__Unstructured[all-docs]
|__Web Search                         |__Brave Search API
|__Type Saftey                        |__Pydantic v2 + TypedDict

