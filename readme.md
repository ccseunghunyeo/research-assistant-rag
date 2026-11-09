# Research Assistant (RAG test)

A small project for testing **RAG (Retrieval-Augmented Generation)** with LangChain.
Before the LLM answers, it pulls real text from **Wikipedia** and **DuckDuckGo**, so its answers are based on sources rather than only on what the model remembers.

## Files

| File | What it does |
|---|---|
| `main.py` | Research assistant. An agent decides when to search Wikipedia or DuckDuckGo, writes a summary with sources, and can save it to a file. |
| `pseudocode.py` | Quiz generator. Gets text about a topic from Wikipedia and DuckDuckGo, asks the LLM for a multiple-choice question based on that text, and checks your answer. |
| `tools.py` | The tools both scripts use: `search` (DuckDuckGo), `wikipedia`, and `save_text_to_file`. |
| `requirements.txt` | Python packages to install. |

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project folder with your NVIDIA API key (you can get one at build.nvidia.com):

```
NVIDIA_API_KEY=your-key-here
```

`.env` is listed in `.gitignore`, so the key never gets committed.

## Usage

```bash
python main.py        # ask a research question
python pseudocode.py  # practise with multiple-choice questions (type "exit" to quit)
```

Results are appended to `research_output.txt` in the folder you run the command from.

## How the model is configured

- Model: `deepseek-ai/deepseek-v4.1-flash`, served through NVIDIA's OpenAI-compatible API (`langchain_openai.ChatOpenAI`).
- Output is parsed into Pydantic models (`ResearchResponse`, `QuizQuestion`), so the results are structured instead of free text.

## Known limitations

- DuckDuckGo sometimes rate-limits searches. The quiz then uses only the Wikipedia text.
- Wikipedia results are cut to 1000 characters to keep token use low, so detailed topics may lose some context.
