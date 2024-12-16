# LONGPIBENCH: A Benchmark for Evaluating Positional Bias in Long-Context LLMs

## Overview

This project provides an implementation and benchmarking framework for **LONGPIBENCH**, a dataset designed to evaluate positional biases in large language models (LLMs) when processing long contexts. The benchmark investigates two types of positional bias:

1. **Absolute Position Bias**: How the location of relevant information within the input sequence affects model performance.
2. **Relative Position Bias**: How the spacing between multiple relevant information pieces impacts the model's ability to process and utilize them.

Our key conclusions:
- Most LLMs exhibit robustness to **absolute positional bias**, reducing the "lost in the middle" issue.
- **Relative positional bias** remains a significant challenge, especially for retrieval-oriented tasks.

The benchmark includes tasks such as Table SQL, Code Completion, and Wiki Retrieval, spanning input lengths from 32K to 256K tokens.

---

## Data Format

Each instance in the benchmark follows this JSON structure:

```json
{
    "seed_id": "unique_identifier",
    "question": "Specific task description, often including example code snippets and instructions.",
    "default_prompt": {
        "system_prompt": "Prompt setting the role and task for the LLM.",
        "user_message": "Detailed query with context, including task requirements."
    },
    "answers": ["Expected model output or solution."],
    "relevant_element": [
        "Metadata about relevant elements in the context, such as API paths, documentation snippets, and their descriptions."
    ],
    "level": "Complexity level (e.g., level 1).",
    "type": "Task type (e.g., absolute or relative bias testing).",
    "token_level": "Maximum token capacity.",
    "token_length": "Actual token length of the input.",
    "context": "Detailed context, such as code snippets or documents relevant to the task.",
    "query_head_prompt": "Prompt template with the query at the beginning of the context.",
    "query_tail_prompt": "Prompt template with the query at the end of the context."
}
```

---

## How to Use

### Setup

1. Run the `setup.sh` script to install dependencies and download the data:
   ```bash
   bash setup.sh
   ```
2. Configure the environment:
   - Add your **API KEY** and **BASE URL** to the `.env` file.

### Evaluation

Evaluate the benchmark on different LLMs using the provided scripts:
- To evaluate on the **Gemini** model:
  ```bash
  bash script/eval_gemini.sh <seed_num>
  ```
- To evaluate on the **Claude** model:
  ```bash
  bash script/eval_claude.sh <seed_num>
  ```

Replace `<seed_num>` with the specific seed ID of the instance you wish to test.

### Testing Models

These scripts support evaluation across a variety of tasks included in LONGPIBENCH. Use the outputs to analyze model performance and assess positional bias.
