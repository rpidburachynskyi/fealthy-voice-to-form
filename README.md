# Automated Form Filling Based on Voice Input

Automated form filling solution that processes Ukrainian voice recordings through ASR, uses combinations of LLM calls with prompts to extract defined named entities, applies specific field postprocessing, and performs a unified business search in Elasticsearch to identify names relevant to those mentioned in the input voice recording and automatically fill the predefined form that holds details about specific financial operation.

## Prerequisites

- Docker

## Setup

1. Create a `.env` file in the project root. Required variables are listed in `.env.example`. For demo purposes, only `OPENAI_API_KEY` and `ELASTICSEARCH_URL` are required. API endpoints and tokens are needed for production.

2. Build and start the application:
   ```bash
   docker-compose up --build
   ```

3. Wait for Elasticsearch to be ready (approximately 30 seconds).

4. Initialize Elasticsearch with required data by running from the `myapp` container:
   ```bash
   docker exec -it myapp python _helpers/docker/initialize_elasticsearch.py
   ```

## Usage

Send a POST request to the API endpoint with an audio file:

```bash
curl --location 'http://localhost:8080' \
  --form 'file=@"./voice-to-text-test1.mp3"'
```

Audio content example: 
1. "Купив з карти монобанку хліб та молоко на 75 гривень 18 копійок в сільпо 2 години 37 хвилин тому." ([voice-to-text-test1.mp3](./voice-to-text-test1.mp3))
2. "Брав за 5 євро лате в чоко 15 хвилин назад. Додай категорію ресторани і мітку кава. Карта універсальна." ([voice-to-text-test2.mp3](./voice-to-text-test2.mp3))

## Evaluation

The evaluation process tests the processing flow components against ground truth data. The `eval.py` script processes all test cases from `eval_data.csv` and generates comparison results in `eval.csv` with expected vs obtained data for each test case:

```bash
python _eval/eval.py
```

The `metric.py` script calculates and displays accuracy metrics from `eval.csv`, including time, description, currency, amount, and business matching metrics:

```bash
python _eval/metric.py
```

## Project Structure

- `src/` - Main application code
  - `main.py` - API entry point and processing orchestration
  - `gpt.py` - LLM integration and ASR
  - `prompts.py` - LLM prompts for entity extraction
  - `endpoints.py` - API endpoints for fetching user data
  - `postprocessing.py` - Field-specific postprocessing
  - `validation.py` - Response validation and merging
  - `nlp/` - Text normalization and transliteration
- `elastic/` - Elasticsearch client and business search
- `_helpers/` - Helper code and variables for isolated demo purposes
  - `api_demo_data/` - Demo data for categories, labels, accounts
  - `docker/` - Initialize Elasticsearch index and populate with data
  - `elasticsearch/` - Scripts for populating Elasticsearch
- `_eval/` - Evaluation of data processing components performance
  - `eval_data.csv` - Ground truth dataset
  - `eval.py` - Generates comparison results (expected vs obtained)
  - `metric.py` - Calculates accuracy metrics from obtained `eval.csv`
