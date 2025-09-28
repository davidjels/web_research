"""
Deep Research: Topic-by-Topic Data Collection
Comprehensive research on topics identified during discovery phase
"""

import json
import os
import time
import csv
import re
import sys
import argparse
import concurrent.futures
import threading
from google import genai
from google.genai import types
from language_config import add_language_args, get_language_config, ensure_folder_exists

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use system environment variables

# --- Configuration ---
try:
    api_key = os.environ["GOOGLE_API_KEY"]
    client = genai.Client(api_key=api_key)
except KeyError:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    exit()

# Model configuration
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-2.5-pro")
print(f"🤖 Using model: {MODEL_NAME}")

# Thread-safe file writing
file_lock = threading.Lock()
log_lock = threading.Lock()
existing_urls = set()

# Audit logging configuration
AUDIT_LOG_DIR = "findings/logs"
AUDIT_LOG_FILE = os.path.join(AUDIT_LOG_DIR, "gather_gemini_responses.jsonl")
RUN_TIMESTAMP = time.strftime('%Y%m%d_%H%M%S')
GATHER_LOG_FILE = os.path.join(AUDIT_LOG_DIR, f"gather_run_{RUN_TIMESTAMP}.md")


def log_raw_response(call_type: str, metadata: dict, response_text: str):
    """Persist raw Gemini responses for auditing/debugging."""
    os.makedirs(AUDIT_LOG_DIR, exist_ok=True)
    payload = {
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "call_type": call_type,
        "metadata": metadata,
        "response_text": response_text,
    }

    serialized = json.dumps(payload, ensure_ascii=False)

    with log_lock:
        with open(AUDIT_LOG_FILE, 'a', encoding='utf-8') as handle:
            handle.write(serialized + "\n")


def init_gather_log(topics: list[dict]):
    """Write header for gather narrative log."""
    os.makedirs(AUDIT_LOG_DIR, exist_ok=True)
    with open(GATHER_LOG_FILE, 'w', encoding='utf-8') as log:
        log.write(f"# Gather Run {RUN_TIMESTAMP}\n\n")
        log.write(f"**Model:** {MODEL_NAME}\n\n")
        log.write(f"**Topics queued:** {len(topics)}\n\n")


def append_gather_log(topic: str, query: str, status: str, findings: list[dict]):
    """Append narrative details for each query processed."""
    with log_lock:
        with open(GATHER_LOG_FILE, 'a', encoding='utf-8') as log:
            log.write(f"## Topic: {topic}\n")
            log.write(f"- **Query:** {query}\n")
            log.write(f"- **Status:** {status}\n")
            log.write(f"- **Findings recorded:** {len(findings)}\n")
            if findings:
                log.write("- **Notable URLs:**\n")
                for result in findings[:5]:
                    url = result.get('url', 'Unknown URL')
                    title = result.get('title', 'Untitled')
                    log.write(f"  - [{title}]({url})\n")
            log.write("\n")


def finalize_gather_log(summary: dict):
    with open(GATHER_LOG_FILE, 'a', encoding='utf-8') as log:
        log.write("---\n\n")
        log.write("## Run Summary\n")
        for label, value in summary.items():
            log.write(f"- **{label}:** {value}\n")
        log.write("\n")

def _parse_topics_from_markdown(markdown_path: str) -> list:
    """Extract researcher-defined topics from a markdown file."""
    if not os.path.exists(markdown_path):
        return []

    topics = []
    current_topic = None

    with open(markdown_path, 'r', encoding='utf-8') as handle:
        for raw_line in handle:
            line = raw_line.rstrip()

            topic_match = re.match(r'##\s+Topic\s+\d+:\s*(.+)', line)
            if topic_match:
                if current_topic and current_topic["queries"]:
                    topics.append(current_topic)

                current_topic = {
                    "name": topic_match.group(1).strip(),
                    "queries": [],
                    "duration": 5,
                }
                continue

            if not current_topic:
                continue

            if line.startswith('Duration:'):
                duration_match = re.search(r'(\d+)', line)
                if duration_match:
                    current_topic["duration"] = int(duration_match.group(1))
                continue

            if line.strip().startswith('- '):
                query_text = line.strip()[2:].strip()
                if query_text:
                    current_topic["queries"].append(query_text)

        # Close out final block
        if current_topic and current_topic["queries"]:
            topics.append(current_topic)

    return topics


def _parse_topics_from_coded_themes(language: str = 'en') -> list:
    """Parse meta-themes from the latest coded analysis JSON."""
    # Find the most recent themes file
    coded_dir = f"findings/2_coded-{language}"
    if not os.path.exists(coded_dir):
        return []

    theme_files = [f for f in os.listdir(coded_dir) if (f.startswith('themes_') or f == 'themes.json') and f.endswith('.json')]
    if not theme_files:
        return []

    # Get the most recent file
    latest_file = max(theme_files)
    theme_path = os.path.join(coded_dir, latest_file)

    try:
        with open(theme_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        themes = data.get('themes', [])
        topics = []

        for theme in themes:
            meta_theme_name = theme.get('meta_theme_name', 'Unnamed Theme')
            description = theme.get('description', '')
            child_themes = theme.get('child_themes', [])
            metrics = theme.get('metrics', {})

            # Create comprehensive queries based on meta-theme and child themes
            queries = []

            # Base queries from meta-theme
            base_terms = _extract_search_terms_from_theme(meta_theme_name, description)
            queries.extend(base_terms)

            # Enhanced queries from child themes
            for child in child_themes:
                child_name = child.get('name', '')
                child_desc = child.get('description', '')
                child_terms = _extract_search_terms_from_theme(child_name, child_desc)
                queries.extend(child_terms)

            # All queries for this meta-theme (includes child themes)
            topics.append({
                "name": meta_theme_name,
                "queries": queries[:15],  # Reasonable limit per theme
                "child_themes": len(child_themes),
                "metrics": metrics
            })

        return topics

    except Exception as e:
        print(f"⚠️ Error parsing coded themes: {e}")
        return []

def _extract_search_terms_from_theme(theme_name: str, description: str) -> list:
    """Extract targeted search queries from theme content."""
    queries = []

    # Clean theme name for search
    clean_name = theme_name.lower().replace('the ', '').replace('of ', '').replace('and ', '')

    # Base queries
    queries.extend([
        f"{clean_name} fertility journey experiences",
        f"{clean_name} trying to conceive stories",
        f"{clean_name} IVF experiences forum",
        f"{clean_name} infertility support reddit"
    ])

    # Extract key concepts from description
    key_terms = []
    if 'anxiety' in description.lower():
        key_terms.extend(['fertility anxiety personal stories', 'two week wait anxiety experiences'])
    if 'grief' in description.lower():
        key_terms.extend(['fertility grief support', 'miscarriage grief stories'])
    if 'financial' in description.lower():
        key_terms.extend(['fertility treatment costs reality', 'IVF financial burden experiences'])
    if 'relationship' in description.lower():
        key_terms.extend(['fertility journey marriage impact', 'partner fertility treatment strain'])
    if 'medical' in description.lower():
        key_terms.extend(['fertility clinic patient experiences', 'doctor fertility treatment communication'])

    queries.extend(key_terms)
    return queries[:6]  # Limit per theme section

def _parse_topics_from_initial_themes(theme_path: str) -> list:
    """Fallback parser that converts AI-generated initial themes into topics."""
    if not os.path.exists(theme_path):
        return []

    topics = []
    with open(theme_path, 'r', encoding='utf-8') as handle:
        content = handle.read()

    topic_blocks = re.findall(r'## .*?(?=## |$)', content, re.DOTALL)
    for block in topic_blocks:
        topic_data = {"name": "", "queries": [], "duration": 5}

        name_match = re.search(r'## Topic \d+:\s*(.+)', block)
        if name_match:
            topic_data["name"] = name_match.group(1).strip()

        duration_match = re.search(r'Duration:\s*(\d+)\s*minutes', block)
        if duration_match:
            topic_data["duration"] = int(duration_match.group(1))

        queries_section = re.search(r'Queries:(.*?)(?=Duration:|$)', block, re.DOTALL)
        if queries_section:
            queries = [
                line.strip('- ').strip()
                for line in queries_section.group(1).split('\n')
                if line.strip().startswith('-')
            ]
            topic_data["queries"] = queries

        if topic_data["name"] and topic_data["queries"]:
            topics.append(topic_data)

    return topics


def read_research_topics(language: str = 'en'):
    """Determine which research topics to run for deep collection."""
    manual_topics = _parse_topics_from_markdown("RESEARCH_TOPICS.md")
    if manual_topics:
        print(f"📄 Loaded {len(manual_topics)} researcher-defined topics from RESEARCH_TOPICS.md")
        return manual_topics

    # Try new hierarchical themes structure
    coded_themes = _parse_topics_from_coded_themes(language)
    if coded_themes:
        print(f"🎯 Loaded {len(coded_themes)} meta-themes from coded analysis")
        return coded_themes

    # Fallback to old structure
    generated_topics = _parse_topics_from_initial_themes(f"findings/2_coded-{language}/initial_themes.md")
    if generated_topics:
        print(f"🧠 Loaded {len(generated_topics)} topics from initial_themes.md")
    return generated_topics

def load_existing_urls(csv_file: str) -> set:
    """Load existing URLs from CSV to prevent duplicates"""
    urls = set()
    if os.path.exists(csv_file):
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'url' in row and row['url']:
                        urls.add(row['url'])
            print(f"   📚 Loaded {len(urls)} existing URLs from {csv_file}")
        except Exception as e:
            print(f"   ⚠️ Could not load existing URLs: {e}")
    return urls

def search_web_simple(query: str, topic: str) -> list:
    """Use Google Search to find content"""
    import datetime
    start_time = datetime.datetime.now()
    print(f"   📡 [{start_time.strftime('%H:%M:%S')}] Searching: '{query[:50]}...'")

    search_tool = types.Tool(google_search=types.GoogleSearch())

    search_prompt = f"""
    Search for personal experiences about: "{query}"

    Find authentic stories from forums, Reddit, or blogs about {topic}.
    Return all HIGH-QUALITY relevant results you find. Prioritize diverse, authentic personal experiences.

    IMPORTANT: Return as many good results as you find naturally (could be 3, could be 15, could be 25) but don't exceed 30 results per search to keep processing manageable.

    Format as JSON list with this structure:
    [
      {{
        "url": "full URL",
        "title": "page title",
        "content": "summary of main post content (100-200 words)",
        "comments_summary": "comprehensive summary of community responses/comments/answers including key themes, sentiments, and diverse perspectives (up to 500 words, or 'N/A' for articles/blogs without comments)",
        "source": "reddit or forum or blog",
        "relevance": 0.8
      }}
    ]
    """

    try:
        print(f"   🚀 [{datetime.datetime.now().strftime('%H:%M:%S')}] Calling Gemini Search API...")

        # Use timeout wrapper to prevent hanging
        def make_search_call():
            return client.models.generate_content(
                model=MODEL_NAME,
                contents=search_prompt,
                config=types.GenerateContentConfig(
                    tools=[search_tool]
                )
        )

        # Execute with 60-second timeout
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(make_search_call)
            try:
                response = future.result(timeout=60)  # 60 second timeout
                api_time = datetime.datetime.now()
                print(f"   📥 [{api_time.strftime('%H:%M:%S')}] Search API response received")
            except concurrent.futures.TimeoutError:
                print(f"   ⚠️  [{datetime.datetime.now().strftime('%H:%M:%S')}] Search API timeout after 60 seconds")
                return []

        # Extract JSON from response text
        response_text = response.text.strip()
        print(f"   📝 [{datetime.datetime.now().strftime('%H:%M:%S')}] Raw response: {response_text[:100]}...")
        log_raw_response(
            call_type="search",
            metadata={"query": query, "topic": topic},
            response_text=response_text,
        )

        # Try to find JSON in the response
        try:
            # Look for JSON array pattern
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                results = json.loads(json_str)
                print(f"   🔍 [{datetime.datetime.now().strftime('%H:%M:%S')}] JSON array parsed successfully")
            else:
                print(f"   ⚠️ [{datetime.datetime.now().strftime('%H:%M:%S')}] No JSON array found, trying direct parse")
                results = json.loads(response_text)
        except json.JSONDecodeError as je:
            print(f"   ❌ [{datetime.datetime.now().strftime('%H:%M:%S')}] JSON parse error: {str(je)[:100]}")
            print(f"   📋 Response sample: {response_text[:300]}...")
            # If no valid JSON, create mock results from search
            results = [{
                "url": "https://example.com",
                "title": "Search result for: " + query[:50],
                "content": "Content found via Google Search",
                "comments_summary": "No comments available",
                "source": "search",
                "relevance": 0.7
            }]

        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"   ✅ [{end_time.strftime('%H:%M:%S')}] Found {len(results)} results in {duration:.1f}s")
        return results

    except Exception as e:
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"   ❌ [{end_time.strftime('%H:%M:%S')}] Search error after {duration:.1f}s: {str(e)[:150]}")
        return []

def score_content_simple(content: str, title: str, metadata: dict | None = None) -> dict:
    """Score content for research value and emotional tone"""
    import datetime
    start_time = datetime.datetime.now()
    print(f"      📊 [{start_time.strftime('%H:%M:%S')}] Scoring: '{title[:30]}...'")

    scoring_prompt = f"""
    Analyze this fertility-related content for research value:
    Title: {title}
    Content: {content}

    Rate on these scales and return JSON:

    research_value (1-5): How valuable is this for understanding user needs?
    1=Generic/surface level, 5=Rich insights with specific details

    emotional_tone (-2 to +2): What's the overall emotional trajectory?
    -2=Despair/crisis, -1=Struggle/difficulty, 0=Mixed/neutral, +1=Hope/encouragement, +2=Success/celebration

    detail_level (1-5): How much specific detail does this provide?
    1=Vague, 5=Highly specific with actionable details

    personal_story (true/false): Is this a first-person personal experience?

    Return ONLY a JSON object with these exact fields - analyze the content carefully and provide genuine scores:
    {{
      "research_value": [analyze and score 1-5],
      "emotional_tone": [analyze and score -2 to +2],
      "detail_level": [analyze and score 1-5],
      "personal_story": [true if first-person experience, false otherwise],
      "key_insights": "[what specific insights make this valuable or not]"
    }}

    CRITICAL: Do not use template values - actually analyze the content and provide accurate scores.
    """

    try:
        print(f"      🚀 [{datetime.datetime.now().strftime('%H:%M:%S')}] Calling Gemini API for scoring...")

        # Use timeout wrapper to prevent hanging
        def make_scoring_call():
            return client.models.generate_content(
                model=MODEL_NAME,
                contents=scoring_prompt
            )

        # Execute with 30-second timeout (scoring should be faster than search)
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(make_scoring_call)
            try:
                response = future.result(timeout=30)  # 30 second timeout
                api_time = datetime.datetime.now()
                print(f"      📥 [{api_time.strftime('%H:%M:%S')}] API response received, parsing...")
            except concurrent.futures.TimeoutError:
                print(f"      ⚠️  [{datetime.datetime.now().strftime('%H:%M:%S')}] Scoring API timeout after 30 seconds - using default scores")
                duration = datetime.datetime.now() - start_time
                print(f"      ⏱️  [{datetime.datetime.now().strftime('%H:%M:%S')}] Scoring timeout completed in {duration.total_seconds():.1f}s")
                return {
                    "research_value": 3,  # Default middle score
                    "emotional_tone": "mixed",  # Default neutral tone
                    "summary": "Content scoring timed out - manually review if needed",
                    "reasoning": "API timeout prevented automated scoring"
                }

        # Parse JSON from response text
        response_text = response.text.strip()
        log_raw_response(
            call_type="score",
            metadata=metadata or {"title": title},
            response_text=response_text,
        )

        try:
            # Look for JSON object pattern
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                scores = json.loads(json_str)
                print(f"      🔍 [{datetime.datetime.now().strftime('%H:%M:%S')}] JSON parsed successfully")
            else:
                print(f"      ⚠️ [{datetime.datetime.now().strftime('%H:%M:%S')}] No JSON braces found, trying direct parse")
                scores = json.loads(response_text)
        except json.JSONDecodeError as je:
            # Default scores if parsing fails
            print(f"      ❌ [{datetime.datetime.now().strftime('%H:%M:%S')}] JSON parse error: {str(je)[:100]}")
            print(f"      📋 Response sample: {response_text[:200]}...")
            scores = {"research_value": 3, "emotional_tone": 0, "detail_level": 3, "personal_story": False, "key_insights": "Parse error"}

        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"      ✅ [{end_time.strftime('%H:%M:%S')}] Research Value: {scores.get('research_value', 3)}/5 | Emotional: {scores.get('emotional_tone', 0):+1.0f} | Detail: {scores.get('detail_level', 3)}/5 | Duration: {duration:.1f}s")

        return scores

    except Exception as e:
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"      ❌ [{end_time.strftime('%H:%M:%S')}] Scoring error after {duration:.1f}s: {str(e)[:150]}")
        return {"research_value": 3, "emotional_tone": 0, "detail_level": 3, "personal_story": False, "key_insights": "Error"}

def gather_for_topic(topic_data: dict, csv_file: str, topic_urls: set) -> tuple:
    """Gather data for one topic
    Returns: (findings_count, csv_file_used)
    """
    topic_name = topic_data["name"]
    queries = topic_data["queries"]
    child_themes = topic_data.get("child_themes", 0)
    metrics = topic_data.get("metrics", {})

    print(f"\n🔍 Topic: {topic_name}")
    if child_themes:
        print(f"   📊 Child themes: {child_themes}")
    if metrics:
        print(f"   📈 Prevalence: {metrics.get('prevalence', 'N/A')}/10 | Emotional: {metrics.get('emotional_intensity', 'N/A')}/10")

    findings_count = 0

    for query_index, query in enumerate(queries):
        print(f"   [{query_index + 1}/{len(queries)}] Processing query...")

        # Search
        results = search_web_simple(query, topic_name)

        new_records = []

        # Score and save each result (skip duplicates)
        for result in results:
            url = result.get('url', '')

            # Skip if URL already exists in this topic's file
            if url in topic_urls:
                print(f"      ⏭️ Skipping duplicate URL: {url[:50]}...")
                continue

            score_metadata = {
                "topic": topic_name,
                "query": query,
                "url": url,
                "title": result.get('title', ''),
            }
            scores = score_content_simple(result.get('content', ''), result.get('title', ''), metadata=score_metadata)

            # Save to CSV
            with file_lock:
                file_exists = os.path.isfile(csv_file)
                with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow(['topic', 'query', 'url', 'title', 'content', 'comments_summary', 'source', 'relevance', 'research_value', 'emotional_tone', 'detail_level', 'personal_story', 'key_insights', 'timestamp'])

                    writer.writerow([
                        topic_name,
                        query,
                        url,
                        result.get('title', ''),
                        result.get('content', ''),
                        result.get('comments_summary', 'No comments captured'),
                        result.get('source', ''),
                        result.get('relevance', 0.5),
                        scores.get('research_value', 3),
                        scores.get('emotional_tone', 0),
                        scores.get('detail_level', 3),
                        scores.get('personal_story', False),
                        scores.get('key_insights', ''),
                        time.strftime('%Y-%m-%d %H:%M:%S')
                    ])

                # Add URL to this topic's set
                topic_urls.add(url)

            findings_count += 1
            new_records.append(result)

        status = "new findings" if new_records else ("no new after dedupe" if results else "no results")
        append_gather_log(topic_name, query, status, new_records)

        # Brief pause between queries to avoid rate limits
        if query_index < len(queries) - 1:
            time.sleep(3)

    print(f"   ✅ {topic_name}: {findings_count} findings")
    return findings_count, csv_file

def filter_topics_by_selection(topics: list, selected_indices: list = None) -> list:
    """Filter topics based on user selection."""
    if not selected_indices:
        return topics

    filtered = []
    for i in selected_indices:
        if 1 <= i <= len(topics):
            filtered.append(topics[i-1])  # Convert to 0-based index
        else:
            print(f"⚠️ Invalid theme index: {i} (available: 1-{len(topics)})")

    return filtered

def show_available_themes(topics: list):
    """Display available themes for selection."""
    print("\n📋 Available Meta-Themes:")
    for i, topic in enumerate(topics, 1):
        name = topic["name"]
        metrics = topic.get("metrics", {})
        prevalence = metrics.get("prevalence", "N/A")
        emotional = metrics.get("emotional_intensity", "N/A")
        child_count = topic.get("child_themes", 0)
        query_count = len(topic.get("queries", []))

        print(f"{i}. {name}")
        print(f"   📊 Prevalence: {prevalence}/10 | Emotional: {emotional}/10")
        print(f"   📝 Child themes: {child_count} | Queries: {query_count}")
        print()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Deep research on fertility themes")
    parser.add_argument("--themes", "-t", nargs="+", type=int,
                       help="Specific theme numbers to research (e.g., --themes 1 3)")
    parser.add_argument("--list", "-ls", action="store_true",
                       help="List available themes and exit")
    add_language_args(parser)
    return parser.parse_args()

def main():
    print("\n🔬 Deep Research: Topic-by-Topic Data Collection")

    args = parse_args()

    language_config = get_language_config(args.language)
    print(f"🌐 Language: {language_config['name']} ({args.language})")

    topics = read_research_topics(args.language)
    if not topics:
        print(f"❌ No themes found for language {args.language}")
        print(f"💡 Run 2_coding.py --language {args.language} first to identify themes")
        return

    if args.list:
        show_available_themes(topics)
        return

    # Filter topics if specific ones were selected
    if args.themes:
        print(f"🎯 Selected themes: {args.themes}")
        topics = filter_topics_by_selection(topics, args.themes)
        if not topics:
            print("❌ No valid themes selected")
            return
    else:
        show_available_themes(topics)
        print(f"🚀 Processing all {len(topics)} themes (use --themes 1 2 3 to select specific ones)")

    output_dir = ensure_folder_exists(3, 'gather', args.language)

    print(f"🤖 Model: {MODEL_NAME}")
    print(f"📁 Output directory: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)

    # Initialize narrative log
    init_gather_log(topics)

    print(f"🚀 Collecting data for {len(topics)} topics")
    print(f"💾 Creating separate CSV file for each theme")

    # Prepare topic-CSV file mappings
    topic_files = []
    for i, topic in enumerate(topics, 1):
        # Create numbered CSV file for each theme
        if args.themes and i in args.themes:
            theme_index = args.themes.index(i) + 1
        else:
            theme_index = i

        csv_file = f"{output_dir}/gathered_data-{theme_index}-{args.language}.csv"

        # Load existing URLs for this specific CSV file
        topic_urls = load_existing_urls(csv_file)

        topic_files.append({
            'topic': topic,
            'csv_file': csv_file,
            'topic_urls': topic_urls,
            'index': theme_index
        })

        print(f"   📄 Theme {theme_index}: {csv_file}")

    # Run topics in parallel
    total_findings = 0
    output_files = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_data = {
            executor.submit(gather_for_topic, data['topic'], data['csv_file'], data['topic_urls']): data
            for data in topic_files
        }

        for future in concurrent.futures.as_completed(future_to_data):
            data = future_to_data[future]
            try:
                findings, csv_file = future.result()
                total_findings += findings
                if csv_file not in output_files:
                    output_files.append(csv_file)
            except Exception as e:
                print(f"❌ {data['topic']['name']} failed: {e}")

    print(f"\n✅ Collection complete: {total_findings} total findings")
    print(f"📁 Created {len(output_files)} CSV files:")
    for file in output_files:
        print(f"   • {os.path.basename(file)}")
    print("📄 Summary:")
    print(f"   • Topics processed: {len(topics)}")
    print(f"   • New findings appended: {total_findings}")
    print(f"   • Output directory: {os.path.abspath(output_dir)}")
    print(f"   • Audit log: {os.path.abspath(AUDIT_LOG_FILE)}")
    print(f"   • Narrative log: {os.path.abspath(GATHER_LOG_FILE)}")
    print(f"💡 Next step: Run analyze.py to process findings")

    finalize_gather_log({
        "Topics processed": len(topics),
        "Findings appended": total_findings,
        "Output directory": os.path.abspath(output_dir),
        "CSV files created": len(output_files),
    })

if __name__ == "__main__":
    main()
