#!/usr/bin/env python3
"""
Qualitative Coding Phase: One-shot Theme Analysis
Uses Gemini's large context window to analyze all discovery data at once
"""

import os
import time
import json
import pandas as pd
import argparse
from google import genai
from google.genai import types
from language_config import add_language_args, get_language_config, ensure_folder_exists

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


class ThematicAnalyzer:
    """One-shot thematic analysis using large context window."""

    def __init__(self, data_file: str, language: str = 'en'):
        self.data_file = data_file
        self.language = language
        self.language_config = get_language_config(language)
        self.data = self.load_data()
        self.output_dir = ensure_folder_exists(2, 'coded', language)

        # Store timestamp for metadata only
        self.run_timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    def load_data(self):
        """Load discovery data from CSV"""
        print(f"📚 Loading data from {self.data_file}...")
        try:
            df = pd.read_csv(self.data_file)
            print(f"   ✅ Loaded {len(df)} entries")
            return df
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return pd.DataFrame()

    def prepare_data_for_analysis(self):
        """Convert CSV data to readable format for AI analysis"""
        if self.data.empty:
            return ""

        # Create a formatted string with all discovery data
        formatted_data = []
        for idx, row in self.data.iterrows():
            entry = f"""Entry {idx + 1}:
Query: {row.get('query', '')}
Title: {row.get('title', '')}
Theme: {row.get('theme', '')}
Perspective: {row.get('perspective', '')}
Key Insight: {row.get('key_insight', '')}
---"""
            formatted_data.append(entry)

        return "\n\n".join(formatted_data)

    def analyze_themes(self):
        """Perform comprehensive thematic analysis in one shot"""
        print("\n🎯 Starting Thematic Analysis")
        print("=" * 60)

        if self.data.empty:
            print("❌ No data to analyze")
            return None, None

        print(f"📊 Analyzing {len(self.data)} discovery entries...")

        # Prepare data
        formatted_data = self.prepare_data_for_analysis()

        # Create comprehensive analysis prompt following thematic analysis best practices
        prompt = f"""
        You are conducting a rigorous qualitative thematic analysis following established research methodology. Your goal is to identify and interpret patterns of meaning across this fertility journey dataset.

        METHODOLOGICAL APPROACH:
        1. **Immersion and Familiarization**: Engage deeply with the data to absorb content and notice patterns before formal analysis
        2. **Systematic Inductive Coding**: Generate codes derived directly from the data itself, not from pre-existing frameworks
        3. **Theme Development**: Look for patterns and relationships between codes to form coherent themes that tell an interpretive story
        4. **Interpretive Depth**: Move beyond description to interpretation - analyze what the data means, not just what it says
        5. **Reflexivity**: Consider how the fertility experience context shapes meaning and interpretation

        THEME CRITERIA:
        - A theme captures a significant, patterned response or meaning relevant to fertility experiences
        - Themes should be more than topic summaries - they must tell an interpretive story about the data
        - Each theme should be well-supported across multiple data extracts, not just vivid examples
        - Themes should reflect genuine patterns in the dataset as a whole

        ANALYSIS INSTRUCTIONS:
        1. First, immerse yourself in the entire dataset to understand the breadth of experiences
        2. Identify 4-6 META-THEMES that represent the highest-level patterns of meaning across fertility experiences
        3. For each meta-theme, identify SUBSTANTIAL CHILD THEMES that represent distinct but related patterns within that domain
        4. Let the data determine hierarchy naturally - some meta-themes may have many child themes (indicating complexity), others may have few
        5. This natural variation in child theme counts will reveal the relative importance and complexity of each meta-theme
        6. Focus on interpretive analysis that goes beyond surface description
        7. Support themes with specific examples that demonstrate the pattern across participants
        8. Consider power dynamics, emotional processes, and systemic issues that shape experiences
        9. Name themes to reflect their interpretive essence, not just descriptive content

        DISCOVERY DATA:
        {formatted_data}

        Please provide your analysis in this format:

        # Thematic Analysis: Fertility Journey Experiences

        ## Meta-Theme 1: [Interpretive Meta-Theme Name]
        **Analytical Metrics:**
        - Prevalence: [1-10 scale] - How frequently this appears across the dataset
        - Emotional Intensity: [1-10 scale] - How deeply felt/impactful this is for individuals
        - Journey Impact: [1-10 scale] - How much this affects overall fertility journey outcomes
        - Universality: [1-10 scale] - How broadly this is experienced across different demographics
        - Systemic Depth: [1-10 scale] - How much this reveals about underlying systems/structures

        [Interpretive analysis of what this meta-theme reveals about fertility experiences - focus on the overarching pattern]

        ### Child Theme 1.1: [Substantial Child Theme Name]
        [Detailed analysis of this specific aspect within the meta-theme]

        ### Child Theme 1.2: [Another Child Theme Name]
        [Analysis of this distinct but related pattern]

        [Continue with as many child themes as the data actually supports - could be 1, could be 7+]

        ## Meta-Theme 2: [Interpretive Meta-Theme Name]
        [Continue with same hierarchical approach...]

        ## Synthesis
        Provide an interpretive synthesis that explains what these themes collectively reveal about the fertility journey experience, including underlying processes, power dynamics, and systemic issues that shape participants' experiences.
        """

        print("🤖 Calling Gemini for comprehensive analysis...")

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            print("✅ Analysis complete!")
            return response.text, self.extract_themes_for_json(response.text)

        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            return None, None

    def extract_themes_for_json(self, markdown_analysis):
        """Extract structured theme data from markdown analysis for JSON output"""
        print("📝 Extracting structured theme data...")

        # Use AI to convert markdown to structured JSON
        extract_prompt = f"""
        Please convert this thematic analysis into a structured JSON format.

        Extract each major theme and its sub-themes into this JSON structure:

        [
          {{
            "meta_theme_name": "Meta-Theme Title",
            "description": "Overall theme description",
            "metrics": {{
              "prevalence": 8,
              "emotional_intensity": 9,
              "journey_impact": 7,
              "universality": 6,
              "systemic_depth": 8
            }},
            "child_themes": [
              {{
                "name": "Child theme name",
                "description": "Detailed description of this substantial child theme"
              }}
            ]
          }}
        ]

        CRITICAL: This should reflect genuine hierarchical analysis where:
        - Each meta-theme has the number of child themes the data actually supports (1-7+ child themes)
        - Variation in child theme counts naturally shows relative complexity/importance of meta-themes
        - Do not force uniform numbers - let the data determine the structure

        MARKDOWN ANALYSIS TO CONVERT:
        {markdown_analysis}

        Return only the JSON array, no other text.
        """

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=extract_prompt
            )

            # Extract JSON from response
            response_text = response.text.strip()
            start = response_text.find('[')
            end = response_text.rfind(']') + 1

            if start >= 0 and end > start:
                json_str = response_text[start:end]
                themes_data = json.loads(json_str)
                print(f"✅ Extracted {len(themes_data)} themes for JSON")
                return themes_data
            else:
                print("⚠️ Could not extract JSON from response")
                return []

        except Exception as e:
            print(f"⚠️ Error extracting JSON structure: {e}")
            return []

    def save_results(self, markdown_analysis, json_themes):
        """Save both markdown and JSON outputs"""
        if not markdown_analysis:
            print("❌ No analysis to save")
            return

        # Save markdown analysis
        md_path = f"{self.output_dir}/thematic_analysis.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_analysis)
        print(f"📄 Saved markdown analysis: {md_path}")

        # Save JSON themes
        if json_themes:
            json_path = f"{self.output_dir}/themes.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'generated_at': self.run_timestamp,
                    'model': MODEL_NAME,
                    'data_source': self.data_file,
                    'total_entries': len(self.data),
                    'themes': json_themes
                }, f, indent=2, ensure_ascii=False)
            print(f"🔗 Saved JSON themes: {json_path}")



def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Qualitative coding of fertility data")
    add_language_args(parser)
    args = parser.parse_args()

    language_config = get_language_config(args.language)

    print(f"🤖 Using model: {MODEL_NAME}")
    print(f"🌐 Language: {language_config['name']} ({args.language})")

    # Use discovery data with new folder structure
    discovery_file = f"findings/1_discovery-{args.language}/discovery_data-{args.language}.csv"

    if not os.path.exists(discovery_file):
        print(f"❌ Discovery file not found: {discovery_file}")
        print(f"💡 Run 1_discover.py --language {args.language} first to generate discovery data")
        return

    print(f"📊 Using discovery data: {discovery_file}")

    # Initialize analyzer
    analyzer = ThematicAnalyzer(discovery_file, args.language)

    # Perform analysis
    markdown_analysis, json_themes = analyzer.analyze_themes()

    # Save results
    analyzer.save_results(markdown_analysis, json_themes)

    print("\n✅ Thematic Analysis Complete!")
    print(f"📁 Results saved in: {analyzer.output_dir}/")
    print("📄 Summary:")
    print(f"   • Source file: {os.path.abspath(discovery_file)}")
    print(f"   • Entries analyzed: {len(analyzer.data)}")
    if json_themes:
        print(f"   • Themes identified: {len(json_themes)}")
    print(f"   • Output directory: {os.path.abspath(analyzer.output_dir)}")
    print(f"💡 Next step: Run 3_gather.py --language {args.language} for deep research on identified themes")


if __name__ == "__main__":
    main()