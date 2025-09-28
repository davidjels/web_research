#!/usr/bin/env python3
"""
Analysis Phase: Simple One-Shot Analysis per Theme
Processes each gathered data file separately with comprehensive analysis
"""

import os
import csv
import time
import re
import argparse
from pathlib import Path
from google import genai
from language_config import add_language_args, get_language_config, format_filename, get_output_instruction

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- Configuration ---
try:
    api_key = os.environ["GOOGLE_API_KEY"]
    client = genai.Client(api_key=api_key)
except KeyError:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    exit()

MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-2.5-pro")

def find_gather_files(language='en'):
    """Find all CSV files in findings/gather/ directory for specified language"""
    gather_dir = Path(f"findings/3_gather-{language}")
    if not gather_dir.exists():
        print(f"❌ findings/3_gather-{language}/ directory not found")
        return []

    # Look for files with language suffix: gathered_data-1-en.csv, gathered_data-2-es.csv etc.
    pattern = f"gathered_data-*-{language}.csv"
    csv_files = list(gather_dir.glob(pattern))

    # Fallback to files without language suffix if none found
    if not csv_files:
        pattern = "gathered_data-*.csv"
        csv_files = list(gather_dir.glob(pattern))
        # Filter out files that have language suffixes for other languages
        csv_files = [f for f in csv_files if not any(f.name.endswith(f"-{lang}.csv") for lang in ['en', 'es'] if lang != language)]

    return sorted(csv_files)

def extract_theme_name(filename):
    """Extract theme identifier from filename"""
    # gathered_data-1.csv -> "theme-1"
    # gathered_data-2-3.csv -> "theme-2-3"
    match = re.search(r'gathered_data-(.+)\.csv', filename)
    if match:
        return f"theme-{match.group(1)}"
    return filename.stem

def load_csv_data(csv_file):
    """Load and format CSV data for analysis"""
    data_entries = []

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            # Format each row for analysis
            entry = f"""
Row {i}:
Topic: {row.get('topic', 'N/A')}
Query: {row.get('query', 'N/A')}
URL: {row.get('url', 'N/A')}
Title: {row.get('title', 'N/A')}
Content: {row.get('content', 'N/A')}
Comments Summary: {row.get('comments_summary', 'N/A')}
Source: {row.get('source', 'N/A')}
Research Value: {row.get('research_value', 'N/A')}
Emotional Tone: {row.get('emotional_tone', 'N/A')}
Key Insights: {row.get('key_insights', 'N/A')}
---"""
            data_entries.append(entry)

    return "\n".join(data_entries)

def analyze_theme_data(csv_file, theme_name, language='en'):
    """Analyze a single theme's data with comprehensive analysis"""
    print(f"\n📊 Analyzing {csv_file.name}...")
    print(f"🎯 Theme: {theme_name}")
    print(f"🌐 Language: {get_language_config(language)['name']}")

    # Load the CSV data
    formatted_data = load_csv_data(csv_file)

    if not formatted_data:
        print(f"⚠️ No data found in {csv_file}")
        return None

    # Get language-specific instructions
    output_instruction = get_output_instruction(language)
    language_config = get_language_config(language)

    # Create comprehensive analysis prompt
    analysis_prompt = f"""
You are a research analyst specializing in qualitative analysis of personal experiences and user journeys. You have extensive expertise in thematic analysis, emotional intelligence, and extracting actionable insights from personal narratives.

**LANGUAGE INSTRUCTION:** {output_instruction}

**IMPORTANT:** This analysis focuses on {language_config['name']}-language sources, so acknowledge any language/cultural bias in your findings. Start your analysis with a note about this limitation.

**ANALYSIS TASK:**
Analyze the attached fertility journey data to extract deep insights about user experiences, pain points, and unmet needs. Focus on patterns that could inform product development, support services, or policy recommendations.

**ANALYSIS FRAMEWORK - Apply these 6 dimensions:**

1. **EMOTIONAL LANDSCAPE**
   - Identify primary emotions and their intensity throughout journeys
   - Map emotional transitions and triggers
   - Note coping mechanisms and resilience patterns
   - Highlight moments of hope vs despair

2. **PRACTICAL BARRIERS & ENABLERS**
   - Extract specific costs, timeframes, and logistics mentioned
   - Identify system inefficiencies and friction points
   - Note successful strategies and workarounds
   - Catalog resources that proved helpful

3. **INFORMATION & DECISION-MAKING**
   - Assess information gaps and confusion points
   - Identify trusted vs questionable information sources
   - Note decision-making criteria and trade-offs
   - Highlight advice that proved valuable

4. **SOCIAL & RELATIONSHIP DYNAMICS**
   - Analyze support system strengths and weaknesses
   - Identify relationship strain patterns
   - Note community/peer support effectiveness
   - Highlight isolation vs connection themes

5. **SYSTEM NAVIGATION CHALLENGES**
   - Map healthcare system pain points
   - Identify insurance and financial obstacles
   - Note provider relationship issues
   - Highlight systemic inequities or access barriers

6. **JOURNEY STAGE INSIGHTS**
   - Analyze needs by journey stage (early, mid, late, post-treatment)
   - Identify stage-specific vulnerabilities
   - Note transition challenges between stages
   - Highlight successful progression strategies

**BEST PRACTICES FOR ANALYSIS:**

**Credibility Assessment:**
- Weight insights by specificity and detail level
- Consider consistency across multiple accounts
- Note potential bias or extreme cases
- Prioritize first-hand experiences over hearsay

**Pattern Recognition:**
- Look for recurring themes across different sources
- Identify both majority and minority experiences
- Note demographic or contextual variations
- Distinguish between universal vs situational patterns

**Actionable Insights:**
- Focus on modifiable factors rather than fixed constraints
- Identify intervention opportunities
- Consider scalability of solutions
- Prioritize high-impact, addressable pain points

**Contextual Understanding:**
- Consider cultural, geographic, and demographic contexts
- Account for healthcare system variations
- Note temporal factors (policy changes, treatment evolution)
- Recognize intersectional experiences

**OUTPUT STRUCTURE:**
Organize your analysis into:
1. **Executive Summary** (key findings in 3-5 bullet points)
2. **Major Themes** (5-7 primary patterns with supporting evidence)
3. **Critical Pain Points** (ranked by frequency and severity)
4. **Unmet Needs** (gaps in current support/services)
5. **Success Factors** (what works well for positive outcomes)
6. **Recommendations** (3-5 actionable insights for stakeholders)
7. **Notable Quotes** (powerful representative statements)

**ANALYTICAL RIGOR:**
- Support each finding with specific examples
- Quantify patterns where possible ("mentioned in X% of posts")
- Distinguish between correlation and causation
- Acknowledge limitations and potential biases
- Highlight unexpected or counterintuitive findings

Focus on insights that would be valuable to healthcare providers, policymakers, support organizations, or technology developers working in reproductive health.

**DATA TO ANALYZE:**
{formatted_data}

**IMPORTANT:** Reference specific row numbers (Row 1, Row 15, etc.) when citing examples from the data.
"""

    print(f"🤖 Sending to Gemini for analysis...")

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=analysis_prompt
        )

        print(f"✅ Analysis completed successfully")
        return response.text

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return None

def save_analysis(analysis_text, theme_name, language='en'):
    """Save analysis to markdown file with language tag"""
    from language_config import ensure_folder_exists
    output_dir = Path(ensure_folder_exists(4, 'analysis', language))

    # Format filename with language tag
    output_file = output_dir / format_filename(f"analysis-{theme_name}", language, 'md')

    # Add metadata header
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    language_config = get_language_config(language)
    header = f"""# Analysis Report: {theme_name.title()} ({language_config['name']})

**Generated:** {timestamp}
**Model:** {MODEL_NAME}
**Language:** {language_config['name']} ({language})
**Analysis Type:** Comprehensive One-Shot Analysis

---

"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(header + analysis_text)

    print(f"💾 Saved: {output_file}")
    return output_file

def main():
    """Main analysis function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Analyze gathered fertility data")
    add_language_args(parser)
    args = parser.parse_args()

    language_config = get_language_config(args.language)

    print(f"\n📊 Analysis Phase: Comprehensive Theme Analysis")
    print("=" * 60)
    print(f"🤖 Using model: {MODEL_NAME}")
    print(f"🌐 Language: {language_config['name']} ({args.language})")

    # Find all gather files for the specified language
    csv_files = find_gather_files(args.language)

    if not csv_files:
        print(f"❌ No gathered data files found for language '{args.language}' in findings/3_gather-{args.language}/")
        print(f"💡 Run 3_gather.py --language {args.language} first to collect data for this language")
        return

    print(f"\n📁 Found {len(csv_files)} data files to analyze:")
    for csv_file in csv_files:
        theme_name = extract_theme_name(csv_file.name)
        print(f"   • {csv_file.name} → {theme_name}")

    # Analyze each file
    results = []
    for csv_file in csv_files:
        theme_name = extract_theme_name(csv_file.name)

        analysis = analyze_theme_data(csv_file, theme_name, args.language)

        if analysis:
            output_file = save_analysis(analysis, theme_name, args.language)
            results.append(output_file)
        else:
            print(f"⚠️ Skipping {csv_file.name} due to analysis failure")

    # Summary
    print(f"\n✅ Analysis Complete!")
    print(f"📊 Successfully analyzed: {len(results)}/{len(csv_files)} files")
    print(f"🌐 Language: {language_config['name']}")

    if results:
        print(f"\n📄 Generated reports:")
        for result in results:
            print(f"   • {result}")

    print(f"\n📁 All analysis files saved in: findings/4_analysis-{args.language}/")

if __name__ == "__main__":
    main()