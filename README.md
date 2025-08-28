# SCA: Saudi Codes Assistant

SCA (Saudi Codes Assistant) is an advanced AI-powered system designed to assist users with inquiries related to Saudi Arabian codes and regulations. This project leverages Retrieval-Augmented Generation (RAG) to provide accurate and contextually relevant information by combining large language models (LLMs) with a robust knowledge base of Saudi codes.

## Key Features

*   **Intelligent Information Retrieval:** Quickly find answers to complex questions about Saudi codes.
*   **Contextual Understanding:** Utilizes RAG to provide highly relevant and accurate responses.
*   **Extensible Architecture:** Designed with modular components for easy expansion to new domains (e.g., electricity, plumbing).
*   **Multimodal Capabilities:** Supports both text-based and vision-based queries, allowing for analysis of images related to codes (e.g., electrical diagrams, plumbing schematics).

## Technical Architecture

The SCA system is built with a modular and scalable architecture, primarily using Python. It integrates various components to achieve its RAG capabilities:

*   **Orchestrator:** The central component (`orchestrator.py`, `simple_orchestrator.py`) that manages the flow of information, routing queries to appropriate handlers and integrating responses from different services.
*   **Handlers:** Domain-specific modules (`handlers/electricity_handler.py`, `handlers/plumbing_handler.py`) that process queries related to specific code categories. These handlers interact with the RAG engine and LLM models.
*   **LLM Models:** Manages the interaction with large language models (`llm/llm_text_model.py`, `llm/llm_vision_model.py`) for natural language understanding and generation, as well as vision-based processing.
*   **Services:** Provides core functionalities such as embedding generation, image analysis, and vector store management (`services/embedding_provider.py`, `services/image_analyzer.py`, `services/rag_engine.py`, `services/vector_store_builder.py`).
*   **Data Management:** Stores and organizes the Saudi codes knowledge base, including vector stores for efficient retrieval (`data/db`, `data/saudi_codes`).
*   **Utilities:** Helper functions and scripts for various tasks, including building vector stores (`utils/llm_models_utils.py`, `scripts/build_all_vector_stores.py`).

### Technologies Used

*   **Python:** The primary programming language for the entire system.
*   **Langchain:** Used for building and managing the RAG pipeline, including `langchain-core` and `langchain-community`.
*   **FAISS:** A vector database used for storing and retrieving document embeddings.
*   **Sentence Transformers:** For generating embeddings from text.
*   **Requests:** For making HTTP requests.
*   **PyPDF:** For parsing PDF documents.
*   **Python-dotenv:** For managing environment variables.
*   **Other potential libraries:** Depending on the specific LLM and vision models used, additional libraries might be required (e.g., for image processing, specific LLM APIs).


## Project Structure

```
SCA/
├── app.py                  # Main application entry point
├── config.py               # Configuration settings
├── orchestrator.py         # Core logic for query orchestration
├── simple_orchestrator.py  # Simplified orchestrator (if applicable)
├── requirements.txt        # Python dependencies
├── test_RAG.py             # Tests for RAG functionality
├── .env                    # Environment variables (not committed)
├── data/
│   ├── db/                 # Vector stores (e.g., ChromaDB)
│   │   └── electricity/
│   └── saudi_codes/        # Raw Saudi code documents
│       └── electricity/
├── handlers/               # Domain-specific query handlers
│   ├── base_handler.py
│   ├── electricity_handler.py
│   └── plumbing_handler.py
├── llm/                    # Large Language Model integrations
│   ├── llm_text_model.py
│   └── llm_vision_model.py
├── scripts/                # Utility scripts
│   └── build_all_vector_stores.py
├── services/               # Core services for RAG and AI
│   ├── embedding_provider.py
│   ├── handler_factory.py
│   ├── image_analyzer.py
│   ├── image_validator.py
│   ├── rag_engine.py
│   └── vector_store_builder.py
└── utils/                  # General utility functions
    └── llm_models_utils.py
```

