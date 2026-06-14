# AI Code Generator and Explainer

## Overview

AI Code Generator and Explainer is a Generative AI-powered application that converts natural language prompts into executable code and provides detailed explanations of the generated output. The application supports multiple programming languages, offers debugging assistance, and allows users to save generated code files locally.

The project leverages open-source Large Language Models (LLMs) such as CodeLlama and DeepSeek-Coder through Ollama, integrates LangChain for prompt orchestration, and provides a user-friendly interface using Streamlit.

---

## Objectives

* Generate code from plain English descriptions.
* Support multiple programming languages.
* Explain generated code step-by-step.
* Provide debugging recommendations.
* Save generated code files locally.
* Offer an intuitive web-based user interface.

---

## Features

### 1. Natural Language to Code Generation

Users can enter prompts describing the desired functionality, and the AI model generates corresponding code.

**Example Prompt:**

> Create a Python program that finds the largest number in a list.

### 2. Multi-Language Support

Supported languages include:

* Python
* Java
* C++

### 3. Code Explanation

The application explains:

* Purpose of the code
* Functionality of each section
* Logic flow
* Important syntax used

### 4. Debugging Suggestions

The system can:

* Identify potential errors
* Suggest code improvements
* Recommend best practices
* Highlight performance optimizations

### 5. Save Generated Code

Users can save generated code locally in the appropriate file format:

| Language | Extension |
| -------- | --------- |
| Python   | .py       |
| Java     | .java     |
| C++      | .cpp      |

---

## Technology Stack

### Backend

* Python 3.10+
* LangChain
* Ollama
* CodeLlama / DeepSeek-Coder

### Frontend

* Streamlit

### AI Models

* CodeLlama
* DeepSeek-Coder

### Supporting Libraries

* LangChain Community
* Python-dotenv
* Pydantic
* Requests

---

## System Architecture

```text
User Prompt
     │
     ▼
Streamlit UI
     │
     ▼
LangChain Prompt Chain
     │
     ▼
Ollama
(CodeLlama / DeepSeek-Coder)
     │
     ├── Generate Code
     ├── Explain Code
     └── Debug Suggestions
     │
     ▼
Output Display
     │
     ▼
Save Code File
```

---

## Project Structure

```text
AI-Code-Generator/
│
├── app.py
├── requirements.txt
├── models/
│
├── chains/
│   ├── code_generator.py
│   ├── code_explainer.py
│   └── debugger.py
│
├── utils/
│   ├── file_handler.py
│   └── prompt_templates.py
│
├── generated_code/
│
└── README.md
```

---

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/your-username/ai-code-generator.git
cd ai-code-generator
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
```

Activate environment:

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Ollama

Download and install Ollama from the official website.

Pull a coding model:

```bash
ollama pull codellama
```

or

```bash
ollama pull deepseek-coder
```

### Step 5: Run Ollama

```bash
ollama serve
```

### Step 6: Launch Streamlit

```bash
streamlit run app.py
```

---

## User Interface

### Prompt Input Area

Allows users to enter a natural language description of the desired program.

### Programming Language Selector

Dropdown menu for selecting:

* Python
* Java
* C++

### Output Display

Displays:

* Generated Code
* Code Explanation
* Debugging Suggestions

### Save Button

Stores generated code in the local system.

---

## LangChain Workflow

### Code Generation Chain

Input:

```text
Create a C++ program to sort an array using quick sort.
```

Output:

```cpp
// Generated Quick Sort Code
```

### Explanation Chain

Input:

```text
Generated Code
```

Output:

```text
Step-by-step explanation of the code.
```

### Debugging Chain

Input:

```text
Generated Code
```

Output:

```text
Suggestions for optimization and debugging.
```

---

## Expected Output Example

### User Prompt

```text
Create a Python function to check if a number is prime.
```

### Generated Code

```python
def is_prime(n):
    if n <= 1:
        return False

    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False

    return True
```

### Explanation

1. The function accepts an integer input.
2. Numbers less than or equal to 1 are not prime.
3. The loop checks divisibility up to the square root.
4. If divisible, the function returns False.
5. Otherwise, it returns True.

### Debug Suggestions

* Add input validation.
* Include unit tests.
* Handle negative values explicitly.

---

## Future Enhancements

* Support additional programming languages.
* Code optimization recommendations.
* Syntax highlighting.
* Export as ZIP package.
* Chat-based coding assistant.
* Integration with GitHub repositories.

---

## Learning Outcomes

By completing this project, developers will gain experience in:

* Generative AI application development
* Prompt engineering
* LangChain workflows
* Streamlit interface design
* Local LLM deployment using Ollama
* AI-powered code generation systems

---

## Conclusion

The AI Code Generator and Explainer project demonstrates how Generative AI can assist developers by automating code generation, providing explanations, and offering debugging support. Using open-source models and local deployment, the application ensures privacy, flexibility, and accessibility for learning and development purposes.
