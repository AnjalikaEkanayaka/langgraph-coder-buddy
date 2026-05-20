# LangGraph Coder Buddy

An AI-powered multi-agent code generation system built using **LangGraph**, **LangChain**, and **Groq LLMs**.

This project simulates a small AI software development team where multiple AI agents collaborate together to:

1. Understand a user request
2. Plan the project
3. Design the project structure
4. Generate source code files
5. Review generated files
6. Automatically request fixes when issues are detected

The system is designed as a beginner-friendly learning project to understand:

- LangGraph workflows
- Multi-agent AI systems
- State-based agent communication
- Structured outputs using JSON
- AI code generation pipelines
- Reviewer / feedback loops
- Prompt engineering
- Guardrails for LLM systems

---

# Project Overview

Instead of using a single AI prompt to generate an entire project, this application separates the workflow into multiple specialized AI agents.

Each agent has a dedicated responsibility.

## Multi-Agent Workflow

```text
User Request
     ↓
Planner Agent
     ↓
Architect Agent
     ↓
Coder Agent
     ↓
Reviewer Agent
     ↓
Fix Loop (if needed)
     ↓
Final Generated Project
```

This architecture mimics a real software engineering workflow.

---

# Features

## Current Features

- Multi-agent workflow using LangGraph
- Planner agent for project planning
- Architect agent for task and file generation
- Coder agent for file generation
- Reviewer agent for validation
- Automatic reviewer → coder feedback loop
- File-by-file generation
- Safe file writing system
- Generated project output folders
- JSON structured task generation
- Debug logging for agent flow visibility
- Infinite loop prevention for reviewer fixes

---

# Tech Stack

## Core Technologies

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| LangGraph | Multi-agent workflow orchestration |
| LangChain | LLM integrations and tooling |
| Groq API | LLM provider |
| Llama Models | Code generation and reasoning |
| VS Code | Development environment |
| uv | Python package and environment manager |

---

# Project Structure

```text
langgraph-coder-buddy/
│
├── app/
│   ├── agents/
│   │   ├── planner.py
│   │   ├── architect.py
│   │   ├── coder.py
│   │   └── reviewer.py
│   │
│   ├── tools/
│   │   └── file_tools.py
│   │
│   ├── graph.py
│   ├── llm.py
│   └── state.py
│
├── generated/
│   └── <generated projects>
│
├── main.py
├── hello_groq.py
├── pyproject.toml
├── .env
└── .gitignore
```

---

# Installation and Setup

## 1. Clone Repository

```bash
git clone <your_repo_url>
cd langgraph-coder-buddy
```

---

## 2. Create Virtual Environment

Using uv:

```bash
uv venv
```

Activate environment:

### PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### CMD

```cmd
.venv\Scripts\activate.bat
```

---

# 3. Install Dependencies

```bash
uv pip install langgraph langchain langchain-groq python-dotenv
```

---

# 4. Configure Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

Get your API key from:

https://console.groq.com/

---

# 5. Run Application

```bash
python main.py
```

---

# How The System Works

# 1. User Request

The application starts from:

```python
user_request = input("What do you want to build?")
```

Example:

```text
simple to do app using html css and js
```

This request becomes the starting state for the LangGraph workflow.

---

# 2. Planner Agent

File:

```text
app/agents/planner.py
```

## Purpose

The Planner agent:

- Understands the user request
- Creates a high-level software plan
- Decides overall features and structure

## Example Output

```text
Project: Simple ToDo App
Features:
- Add tasks
- Remove tasks
- Mark tasks completed
Stack:
- HTML
- CSS
- JavaScript
```

## Important Learning

The planner creates:

- Human-readable planning
- High-level reasoning

This is NOT yet machine-friendly.

---

# 3. Architect Agent

File:

```text
app/agents/architect.py
```

## Purpose

The Architect converts the planner output into structured engineering tasks.

Instead of paragraphs, it produces JSON.

## Why JSON?

JSON is machine-readable.

The Coder agent can easily loop through tasks.

## Example Output

```json
{
  "tasks": [
    {
      "file_path": "index.html",
      "purpose": "Main HTML structure",
      "requirements": [
        "Link styles.css",
        "Link script.js"
      ]
    }
  ]
}
```

## Key Learning

This demonstrates:

- Structured AI outputs
- JSON-based agent communication
- Machine-friendly workflows

---

# 4. Coder Agent

File:

```text
app/agents/coder.py
```

## Purpose

The Coder agent:

- Reads tasks from the Architect
- Generates actual code
- Writes files into the generated project folder

## Workflow

For each task:

```text
Read task
↓
Call LLM
↓
Generate file content
↓
Save file
```

## Example Generated Files

```text
index.html
styles.css
script.js
README.md
```

---

# 5. Reviewer Agent

File:

```text
app/agents/reviewer.py
```

## Purpose

The Reviewer validates generated files.

It checks:

### HTML Files

- Must contain HTML structure
- Must not contain CSS or JS

### CSS Files

- Must only contain CSS
- Must not contain HTML or JS

### JavaScript Files

- Must only contain JS
- Must not contain HTML or CSS

## Auto Fix Workflow

If Reviewer detects issues:

```text
Reviewer
↓
Requests fix
↓
Coder regenerates file
```

This creates a self-correcting AI workflow.

---

# LangGraph Workflow

File:

```text
app/graph.py
```

## Current Graph Flow

```text
Planner
   ↓
Architect
   ↓
Coder
   ↓
Reviewer
   ↓
Fix Loop (if needed)
   ↓
END
```

## Important Learning

LangGraph allows:

- State sharing
- Multi-agent routing
- Conditional flows
- Loops
- AI workflow orchestration

---

# State System

File:

```text
app/state.py
```

## What Is State?

State is shared memory between agents.

Each agent:

- Reads state
- Updates state
- Passes state forward

## Example State Fields

```python
user_request
plan
tasks
current_task_index
created_files
fix_file_path
fix_reason
fix_attempts
```

---

# Safe File System

File:

```text
app/tools/file_tools.py
```

## Purpose

Prevents unsafe file writing.

The system only allows writing inside:

```text
generated/
```

## Important Security Learning

This prevents dangerous paths like:

```text
../../Windows/System32
```

---

# Debugging Features

The project includes debugging logs:

```text
[Planner] Creating plan...
[Architect] Creating file tasks...
[Coder] Generating: index.html
[Reviewer] Checking last written file...
```

These logs help understand:

- Which agent is currently running
- Where failures occur
- How the workflow progresses

---

# Generated Projects

Generated applications are stored in:

```text
generated/<project-name>/
```

Example:

```text
generated/simple_to_do_app/
```

---

# Example Prompt

```text
Create a simple to do app using html css and js
```

---

# Important Concepts Learned During Development

## 1. Multi-Agent Systems

Breaking complex work into specialized AI agents.

---

## 2. Structured Outputs

Using JSON for machine-readable communication.

---

## 3. Prompt Engineering

Improving prompts to:

- reduce hallucinations
- avoid duplicate tasks
- enforce strict outputs

---

## 4. AI Guardrails

Adding:

- reviewer checks
- validation rules
- fix loops
- safe file writing

---

## 5. LLM Reliability Problems

Real-world AI systems may:

- generate invalid JSON
- hallucinate files
- duplicate outputs
- mix HTML/CSS/JS incorrectly

The project demonstrates how to handle these problems.

---

# Challenges Encountered

## Invalid JSON

Architect sometimes generated malformed JSON.

### Solution

- Added stricter prompts
- Added JSON extraction logic
- Added debug printing

---

## Duplicate Tasks

Architect sometimes repeated files.

### Solution

- Added deduplication logic
- Added stricter architect rules

---

## Mixed File Contents

Coder sometimes generated:

- HTML inside CSS files
- CSS inside JS files
- JS inside HTML files

### Solution

- Added strict file-type rules
- Added Reviewer validation
- Added auto-fix loop

---

## Infinite Reviewer Loops

Reviewer sometimes repeatedly rejected files.

### Solution

Added:

```python
fix_attempts
```

to prevent endless loops.

---

# Future Improvements

Potential future upgrades:

- Better structured output validation using Pydantic
- Stronger reviewer intelligence
- Functional browser testing
- Unit test generation
- Docker support
- Streamlit UI
- Multi-model routing
- OpenAI / Gemini / Ollama support
- Memory systems
- Tool-calling agents
- Retrieval-Augmented Generation (RAG)
- Autonomous debugging

---

# Important Notes

## Groq Free Tier

This project currently uses Groq free-tier APIs.

To avoid excessive usage:

- max_tokens limits are used
- file-by-file generation is used
- reviewer loops are limited

---

# Git Workflow Used

Typical workflow:

```bash
git add .
git commit -m "message"
git push
```

---

# Learning Outcomes

This project teaches:

- LangGraph fundamentals
- Multi-agent architecture
- LLM orchestration
- JSON structured outputs
- AI reviewer loops
- Prompt engineering
- AI workflow debugging
- State-based systems
- AI guardrails
- Real-world AI engineering challenges

---

# Credits

Project inspired by:

- LangGraph multi-agent architecture concepts
- AI code generation workflows
- Coder Buddy style systems
- Agentic AI engineering patterns

---

# Disclaimer

This project is primarily a learning-focused implementation.

Generated code quality depends on:

- prompts
- model quality
- reviewer strictness
- architecture constraints

The project demonstrates real-world AI engineering workflows and common challenges encountered while building agentic systems.

