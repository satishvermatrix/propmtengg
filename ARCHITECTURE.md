# Application Architecture

## Modular Structure

```
prompt_engg/
├── prompt.py                 # Main application orchestrator
├── utils.py                  # Utility functions (token counting, text processing)
├── document_processor.py     # Document text extraction
├── llm_operations.py        # LLM API calls and prompt generation
├── gradio_interface.py      # UI components and interface logic
├── pyproject.toml           # Dependencies
└── README.md               # Documentation
```

## Module Responsibilities

### 📁 `prompt.py` (Main Orchestrator)
- **Purpose**: Entry point and application coordination
- **Responsibilities**:
  - Load environment variables
  - Initialize and launch the Gradio interface
  - Coordinate between modules

### 🔧 `utils.py` (Utilities)
- **Purpose**: Core utility functions
- **Functions**:
  - `count_tokens()`: Accurate token counting with tiktoken
  - `truncate_text_to_token_limit()`: Smart text truncation
- **Dependencies**: tiktoken

### 📄 `document_processor.py` (Document Handling)
- **Purpose**: Extract text from various file formats
- **Functions**:
  - `extract_text_from_file()`: Multi-format text extraction
- **Supported Formats**: PDF, DOCX, TXT, CSV, XLSX, XLS
- **Dependencies**: PyPDF2, python-docx, pandas, openpyxl

### 🤖 `llm_operations.py` (LLM Operations)
- **Purpose**: All LLM-related operations and API calls
- **Class**: `LLMOperations`
- **Methods**:
  - `generate_summarization_prompt()`: Create AI prompts for summarization
  - `summarize_document_with_prompt()`: Generate document summaries
  - `generate_with_llm()`: Enhanced prompt generation
  - `combine_inputs()`: Structure prompt components
- **Dependencies**: openai, utils

### 🖥️ `gradio_interface.py` (UI Layer)
- **Purpose**: Gradio interface components and user interactions
- **Class**: `GradioInterface`
- **Methods**:
  - `create_interface()`: Build the complete UI
  - `process_uploaded_document()`: Handle document upload workflow
- **Dependencies**: gradio, llm_operations, document_processor, utils

## Data Flow

```
User Input → gradio_interface.py → llm_operations.py → OpenAI API
     ↓
Document Upload → document_processor.py → utils.py → llm_operations.py
     ↓
Results → gradio_interface.py → User Display
```

## Benefits of Modular Structure

### ✅ **Separation of Concerns**
- Each module has a single responsibility
- Clear boundaries between functionality
- Easier to maintain and debug

### ✅ **Reusability**
- Utility functions can be used across modules
- LLM operations are centralized
- Document processing is independent

### ✅ **Testability**
- Each module can be tested independently
- Mock dependencies easily
- Isolated functionality testing

### ✅ **Scalability**
- Easy to add new document formats
- Simple to extend LLM operations
- UI changes don't affect business logic

### ✅ **Code Organization**
- Related functions grouped together
- Clear import structure
- Logical file naming

## Import Dependencies

```
prompt.py
├── gradio_interface.py
    ├── llm_operations.py
    │   ├── utils.py
    │   └── openai
    ├── document_processor.py
    │   ├── utils.py
    │   ├── PyPDF2
    │   ├── python-docx
    │   └── pandas
    └── gradio
└── dotenv
```

## Future Extensibility

### 🔮 **Easy to Add**:
- New document formats (in `document_processor.py`)
- Additional LLM providers (in `llm_operations.py`)
- New UI components (in `gradio_interface.py`)
- Utility functions (in `utils.py`)

### 🔮 **Easy to Modify**:
- Token limits (in `utils.py`)
- UI layout (in `gradio_interface.py`)
- LLM parameters (in `llm_operations.py`)
- File processing (in `document_processor.py`)
