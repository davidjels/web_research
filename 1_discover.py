"""
Discovery Phase: Theme Identification
Lean discovery to identify key themes before deep research
"""

import os
import time
import csv
import concurrent.futures
import threading
import argparse
from google import genai
from google.genai import types
from language_config import add_language_args, get_language_config, ensure_folder_exists, get_fertility_terms, get_search_instruction

# Load environment variables from .env file
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

# Model configuration
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-2.5-pro")
# Model configuration will be printed in main function after language is determined

# Thread-safe file writing
file_lock = threading.Lock()
existing_urls = set()

# Logging configuration
RUN_TIMESTAMP = time.strftime('%Y%m%d_%H%M%S')
LOG_DIR = "findings/logs"
os.makedirs(LOG_DIR, exist_ok=True)
DISCOVERY_LOG = os.path.join(LOG_DIR, f"discovery_run_{RUN_TIMESTAMP}.md")


def init_log(queries: list[str], language: str = 'en'):
    """Initialize the narrative log for this discovery run."""
    language_config = get_language_config(language)
    with open(DISCOVERY_LOG, 'w', encoding='utf-8') as log:
        log.write(f"# Discovery Run {RUN_TIMESTAMP}\n\n")
        log.write(f"**Model:** {MODEL_NAME}\n\n")
        log.write(f"**Language:** {language_config['name']} ({language})\n\n")
        log.write(f"**Queries:** {len(queries)}\n")
        log.write(f"**Output CSV:** findings/1_discovery-{language}/discovery_data-{language}.csv\n\n")


def log_query_outcome(query: str, status: str, details: str = "", results: list[dict] | None = None):
    """Append query outcome details to the narrative log."""
    results = results or []
    with open(DISCOVERY_LOG, 'a', encoding='utf-8') as log:
        log.write(f"## Query: {query}\n")
        log.write(f"- **Status:** {status}\n")
        if details:
            log.write(f"- **Details:** {details}\n")
        log.write(f"- **Results captured:** {len(results)}\n")
        if results:
            log.write("- **Top Findings:**\n")
            for result in results:
                title = result.get('title', 'Untitled')
                url = result.get('url', 'Unknown URL')
                theme = result.get('theme', 'Unspecified theme')
                log.write(f"  - [{title}]({url}) — *{theme}*\n")
        log.write("\n")


def finalize_log(summary: dict):
    """Write final summary stats to the log."""
    with open(DISCOVERY_LOG, 'a', encoding='utf-8') as log:
        log.write("---\n\n")
        log.write("## Run Summary\n")
        for label, value in summary.items():
            log.write(f"- **{label}:** {value}\n")
        log.write("\n")

def get_discovery_queries(language: str = 'en'):
    """Core discovery queries for theme identification - adapted by language"""
    terms = get_fertility_terms(language)

    if language == 'en':
        return [
            # Core journey experiences
            "fertility journey personal experiences reddit",
            "trying to conceive stories forum",
            "IVF treatment experiences community",
            # Emotional and mental health
            "infertility mental health impact",
            "fertility journey changed me stories",
            # Medical experiences
            "unexplained infertility anxiety",
            "fertility testing experiences",
            "fertility clinic patient stories",
            # Treatment decisions
            "when to start IVF experiences",
            "egg freezing decision stories",
            # Support and community
            "fertility support group helpful",
            "online fertility community experiences",
            # Financial impact
            "fertility treatment costs reality",
            "IVF financial burden stories",
            # Relationship dynamics
            "fertility journey marriage impact",
            "partner fertility treatment support",
            # Loss and trauma
            "miscarriage support stories",
            "pregnancy loss community",
            # Success and hope
            "IVF success after failures",
            "fertility treatment worth it"
        ]
    elif language == 'es':
        return [
            # Core experiences
            "viaje fertilidad experiencias personales foro",
            "tratando de concebir historias comunidad",
            "FIV tratamiento experiencias blog",
            # Emotional and mental health
            "infertilidad impacto salud mental",
            "viaje fertilidad me cambió historias",
            # Medical experiences
            "infertilidad inexplicada ansiedad",
            "pruebas fertilidad experiencias",
            "clínica fertilidad paciente historias",
            # Treatment decisions
            "cuando empezar FIV experiencias",
            "congelación óvulos decisión historias",
            # Support and community
            "grupo apoyo fertilidad útil",
            "comunidad fertilidad online experiencias",
            # Financial impact
            "tratamiento fertilidad costos realidad",
            "FIV carga financiera historias",
            # Relationship dynamics
            "viaje fertilidad impacto matrimonio",
            "pareja apoyo tratamiento fertilidad",
            # Loss and trauma
            "aborto espontáneo apoyo historias",
            "pérdida embarazo comunidad",
            # Success and hope
            "FIV éxito después fracasos",
            "tratamiento fertilidad vale la pena"
        ]
    else:
        # Default to English terms with basic translation attempt
        return [f"{term} experiences stories" for term in terms[:20]]

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
            print(f"   📚 Loaded {len(urls)} existing URLs")
        except Exception as e:
            print(f"   ⚠️ Could not load existing URLs: {e}")
    return urls

def search_for_themes(query: str, language: str = 'en') -> list:
    """Search for content to identify themes"""
    print(f"   🔍 Discovering: '{query[:40]}...'")

    search_tool = types.Tool(google_search=types.GoogleSearch())

    # First, get actual search results
    search_instruction = get_search_instruction(language)
    search_prompt = f"""
    {search_instruction}

    Search for authentic experiences about: "{query}"

    CRITICAL: Use the EXACT URLs returned by search. Do not modify, reconstruct, or change URLs in any way.

    Find diverse perspectives from forums, Reddit, blogs, and support groups.
    Focus on identifying different themes and perspectives within this topic.
    Return up to 5 varied results that show different aspects of this experience.

    Format as JSON list - COPY URLs EXACTLY as they appear in search results:
    [
      {{
        "url": "EXACT URL from search results - DO NOT MODIFY",
        "title": "page title",
        "theme": "main theme this represents (e.g., 'medical anxiety', 'financial burden', 'relationship strain')",
        "perspective": "whose perspective (e.g., 'woman with PCOS', 'male partner', 'single woman')",
        "key_insight": "what unique insight this provides (50-100 words)"
      }}
    ]
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=search_prompt,
            config=types.GenerateContentConfig(
                tools=[search_tool]
            )
        )

        response_text = response.text.strip()
        print(f"   📝 Processing results...")

        import json
        try:
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                results = json.loads(json_str)
            else:
                results = json.loads(response_text)
        except:
            results = []

        print(f"   ✅ Found {len(results)} themes")
        return results

    except Exception as e:
        print(f"   ❌ Search error: {str(e)[:100]}...")
        return []

def discover_themes(language: str = 'en'):
    """Run discovery to identify themes"""
    language_config = get_language_config(language)

    print("\n🔍 Discovery Phase: Theme Identification")
    print(f"🌐 Language: {language_config['name']} ({language})")
    print("🎯 Goal: Identify key themes and perspectives for deep research")

    # Setup output with language-specific folder
    output_dir = ensure_folder_exists(1, 'discovery', language)
    csv_file = os.path.join(output_dir, f"discovery_data-{language}.csv")

    # Load existing URLs
    global existing_urls
    existing_urls = load_existing_urls(csv_file)

    queries = get_discovery_queries(language)
    print(f"📊 Running {len(queries)} discovery queries")
    print(f"💾 Output: {csv_file}")

    # Initialize narrative log
    init_log(queries, language)

    total_themes = 0
    max_results = 100  # Cap at 100 for lean discovery

    # Process queries
    for query in queries:
        if total_themes >= max_results:
            print(f"   🎯 Reached target of {max_results} discoveries")
            break

        results = search_for_themes(query, language)

        if not results:
            log_query_outcome(query, status="error", details="No results returned (see console for errors)")
        else:
            log_query_outcome(query, status="success", details="Results captured", results=results)

        # Save each result
        for result in results:
            if total_themes >= max_results:
                break

            url = result.get('url', '')

            # Skip duplicates
            if url in existing_urls:
                print(f"      ⏭️ Skipping duplicate: {url[:40]}...")
                continue

            # Save to CSV
            with file_lock:
                file_exists = os.path.isfile(csv_file)
                with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow(['query', 'url', 'title', 'theme', 'perspective', 'key_insight', 'timestamp'])

                    writer.writerow([
                        query,
                        url,
                        result.get('title', ''),
                        result.get('theme', ''),
                        result.get('perspective', ''),
                        result.get('key_insight', ''),
                        time.strftime('%Y-%m-%d %H:%M:%S')
                    ])

                existing_urls.add(url)
                total_themes += 1

        # Brief pause between queries
        if total_themes < max_results:
            time.sleep(3)

    print(f"\n✅ Discovery complete: {total_themes} themes identified")
    print(f"📁 Saved to: {csv_file}")
    print("📄 Summary:")
    print(f"   • Queries processed: {len(queries)}")
    print(f"   • Themes captured: {total_themes}")
    print(f"   • Output file: {os.path.abspath(csv_file)}")
    print(f"   • Narrative log: {os.path.abspath(DISCOVERY_LOG)}")

    # Analyze discovered themes
    analyze_themes(csv_file, language)

    finalize_log({
        "Queries processed": len(queries),
        "Themes captured": total_themes,
        "Output file": os.path.abspath(csv_file),
    })

def analyze_themes(csv_file: str, language: str = 'en'):
    """Analyze discovered themes and suggest research topics"""
    language_config = get_language_config(language)
    print("\n🔄 Analyzing discovered themes...")

    if not os.path.exists(csv_file):
        print("❌ No discovery data found")
        return

    # Read discovery data
    themes_data = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            themes_data = list(reader)
    except Exception as e:
        print(f"❌ Error reading themes: {e}")
        return

    if not themes_data:
        print("❌ No themes to analyze")
        return

    print(f"📊 Analyzing {len(themes_data)} discovered themes...")

    # Count theme frequency
    theme_counts = {}
    for row in themes_data:
        theme = row.get('theme', 'Unknown')
        theme_counts[theme] = theme_counts.get(theme, 0) + 1

    # Show top themes
    print("\n📈 Top Discovered Themes:")
    sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
    for theme, count in sorted_themes[:10]:
        print(f"   • {theme}: {count} occurrences")

    # Count perspectives
    perspective_counts = {}
    for row in themes_data:
        perspective = row.get('perspective', 'Unknown')
        perspective_counts[perspective] = perspective_counts.get(perspective, 0) + 1

    print("\n👥 Key Perspectives Found:")
    sorted_perspectives = sorted(perspective_counts.items(), key=lambda x: x[1], reverse=True)
    for perspective, count in sorted_perspectives[:10]:
        print(f"   • {perspective}: {count} occurrences")

    print(f"\n💡 Next step: Run 2_coding.py --language {language} to transform discovery data into coded themes")

def main():
    """Main function with language support"""
    parser = argparse.ArgumentParser(description="Discovery phase for fertility research")
    add_language_args(parser)
    args = parser.parse_args()

    language_config = get_language_config(args.language)

    print(f"🤖 Using model: {MODEL_NAME}")
    print(f"🌐 Language: {language_config['name']} ({args.language})")

    discover_themes(args.language)

if __name__ == "__main__":
    main()
