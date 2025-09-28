# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Web research tool that uses Google's Gemini API to gather and analyze data from online forums and blogs about specific topics. The project consists of two main scripts:
- `gather_data.py`: Searches for and collects personal experiences from forums, storing them in a CSV file
- `analyze_data.py`: Processes the collected data and generates a comprehensive analysis report with citations

## Development Setup

### Environment Management
This project uses UV for dependency management. To set up the environment:
```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv sync
```

### Environment Variables
The project requires a Google API key to be set:
- Set `GOOGLE_API_KEY` environment variable (note: `.env` file currently uses `GEMINI_API_KEY` which needs to be updated to `GOOGLE_API_KEY` for the scripts to work)

## Running the Three-Stage Research Pipeline

### Stage 1: Data Collection
```bash
python gather.py
```
- Auto-detects RESEARCH_BRIEF.md (single topic) or RESEARCH_TOPICS.md (multi-topic)
- Collects raw data with sentiment and quality scoring
- Saves to `findings/raw/raw_[single|multi]_TIMESTAMP.csv`

### Stage 2: Post-by-Post Analysis
```bash
python analyze.py
```
- Analyzes posts by topic with cross-topic connections
- Filters by quality threshold (default: > 0.3)
- Outputs to `findings/analysis/posts_by_topic/`

### Stage 3: Theme Extraction
```bash
python extract.py
```
- Extracts themes per topic + cross-topic synthesis
- Generates reports in `findings/themes/by_topic/` and `findings/themes/cross_topic/`
- Identifies universal themes and topic relationships

## Key Architecture Notes

### Data Flow
1. **Query Generation**: Uses Gemini to generate diverse search queries from a base topic
2. **Data Gathering**: Uses GoogleSearchRetriever tool to find relevant content
3. **Storage**: Appends findings to CSV with source query, URL, and content
4. **Analysis**: Reads all CSV data and generates a synthesized report with citations

### Important Configuration Variables
- `CSV_FILE`: Output file for gathered data (default: "findings.csv")
- `MAIN_TOPIC`: Base topic for research (currently: "IVF experiences and fertility treatments")
- `RUN_DURATION_MINUTES`: How long to run the gathering phase (default: 5)

### Error Handling
Both scripts check for the `GOOGLE_API_KEY` environment variable and exit gracefully if not found. The analysis script also handles missing CSV file scenarios.