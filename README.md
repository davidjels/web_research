# Web Research Pipeline

Data-driven qualitative research pipeline using systematic discovery and coding methodology.

## Quick Start

```bash
# Install dependencies
uv sync

# Set API key and model
export GOOGLE_API_KEY="your-key"
export GEMINI_MODEL="gemini-2.5-pro"  # or gemini-2.5-flash for faster/cheaper

# Run pipeline
python 1_discover.py   # Lean discovery to identify themes
python 2_coding.py     # Iterative qualitative coding with hierarchical themes
python 3_gather.py     # Deep research on discovered themes
python 4_analyze.py    # Structured analysis
python 5_synthesize.py # Final synthesis
```

## Pipeline Overview

**Phase 1: Discovery**
- `1_discover.py` - Unbiased theme identification from community data
- `2_coding.py` - Iterative qualitative coding with automatic hierarchical theme development

**Phase 2: Deep Research**
- `3_gather.py` - Topic-by-topic research based on coded themes
- `4_analyze.py` - Post-level structured analysis
- `5_synthesize.py` - Cross-topic synthesis

## Features

- Real Google Search integration
- Evidence-based theme identification
- Systematic qualitative coding methodology
- Structured output with comprehensive scoring
- Data-driven research topics (no assumptions)

## Output

Results saved to `findings/` with discovery data, coded themes, and structured analysis.

Raw Gemini responses from the gather phase are appended to `findings/logs/gather_gemini_responses.jsonl` for auditing and troubleshooting.
