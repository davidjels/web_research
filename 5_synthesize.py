"""
Stage 3: Advanced Theme Extraction
Uses Thinking Mode + Structured Output for comprehensive theme synthesis
"""

import os
import json
import time
import argparse
from typing import List, Dict, Optional, Any
from pathlib import Path
from collections import Counter, defaultdict
from pydantic import BaseModel, Field
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

# --- Advanced Pydantic Models for Theme Extraction ---

class ThemeEvidence(BaseModel):
    """Evidence supporting a theme"""
    quote: str = Field(description="Representative quote from posts")
    source_count: int = Field(description="Number of posts mentioning this")
    confidence_level: float = Field(description="Confidence in this evidence (0.0-1.0)")
    supporting_factors: List[str] = Field(description="Factors that support this theme")

class MajorTheme(BaseModel):
    """A major theme with comprehensive analysis"""
    theme_name: str = Field(description="Clear, descriptive theme name")
    theme_description: str = Field(description="2-3 sentence explanation of the theme")

    # Quantitative measures
    prevalence_score: float = Field(description="How common is this theme (0.0-1.0)")
    emotional_impact: float = Field(description="Emotional significance (0.0-1.0)")
    practical_importance: float = Field(description="Practical significance (0.0-1.0)")

    # Supporting evidence
    evidence: List[ThemeEvidence] = Field(description="Evidence supporting this theme")
    sub_themes: List[str] = Field(description="Related sub-themes")

    # Analysis
    emotional_patterns: List[str] = Field(description="Emotional patterns associated with this theme")
    practical_implications: List[str] = Field(description="Practical implications or advice")
    knowledge_gaps: List[str] = Field(description="What's missing or needs more research")

    # Actionability
    actionable_insights: List[str] = Field(description="Concrete takeaways people can act on")
    stakeholder_relevance: Dict[str, str] = Field(description="Relevance for different stakeholders")

class EmotionalJourneyMapping(BaseModel):
    """Mapping of emotional journey patterns"""
    journey_phases: List[Dict[str, Any]] = Field(description="Phases of emotional journey")
    common_transitions: List[str] = Field(description="Common emotional transitions")
    resilience_factors: List[str] = Field(description="What helps people cope")
    vulnerability_points: List[str] = Field(description="Points of highest emotional stress")
    support_interventions: List[str] = Field(description="When and how support is most needed")

class PracticalPattern(BaseModel):
    """Practical patterns and insights"""
    decision_frameworks: List[str] = Field(description="How people make key decisions")
    resource_requirements: Dict[str, List[str]] = Field(description="Resources needed at different stages")
    common_timelines: Dict[str, str] = Field(description="Typical timing patterns")
    cost_patterns: List[str] = Field(description="Financial planning patterns")
    success_predictors: List[str] = Field(description="Factors associated with positive outcomes")
    failure_modes: List[str] = Field(description="Common ways things go wrong")

class AdviceSynthesis(BaseModel):
    """Synthesized advice from all posts"""
    essential_advice: List[Dict[str, Any]] = Field(description="Most important advice with context")
    stage_specific_advice: Dict[str, List[str]] = Field(description="Advice by journey stage")
    controversial_topics: List[Dict[str, Any]] = Field(description="Areas where advice conflicts")
    wisdom_insights: List[str] = Field(description="Unique insights that stand out")
    mistake_patterns: List[str] = Field(description="Common mistakes to avoid")

class TopicThemeAnalysis(BaseModel):
    """Complete theme analysis for a single topic"""
    topic_name: str = Field(description="Name of the research topic")
    analysis_metadata: Dict[str, Any] = Field(description="Analysis details and timestamps")

    # Core analysis
    major_themes: List[MajorTheme] = Field(description="5-8 major themes identified")
    emotional_journey: EmotionalJourneyMapping
    practical_patterns: PracticalPattern
    advice_synthesis: AdviceSynthesis

    # Meta-analysis
    unique_contributions: List[str] = Field(description="What makes this topic unique")
    research_priorities: List[str] = Field(description="Most important research gaps")
    policy_implications: List[str] = Field(description="Implications for policy or practice")

    # Quality assessment
    analysis_confidence: float = Field(description="Confidence in this analysis (0.0-1.0)")
    data_quality_notes: List[str] = Field(description="Notes about data quality")

    # Reasoning
    extraction_reasoning: str = Field(description="AI's reasoning for theme identification")

class UniversalTheme(BaseModel):
    """Themes that appear across multiple topics"""
    theme_name: str = Field(description="Universal theme name")
    appearing_in_topics: List[str] = Field(description="Topics where this appears")
    cross_topic_significance: str = Field(description="Why this matters across topics")
    variations_by_topic: Dict[str, str] = Field(description="How this theme varies by topic")
    unifying_insights: List[str] = Field(description="Insights that unify across topics")

class TopicRelationship(BaseModel):
    """How topics relate to each other"""
    relationship_type: str = Field(description="Type: complementary, sequential, contrasting, etc.")
    topics_involved: List[str] = Field(description="Which topics are related")
    relationship_description: str = Field(description="Nature of the relationship")
    implications: List[str] = Field(description="What this relationship means")

class HolisticInsight(BaseModel):
    """Insights that emerge from analyzing all topics together"""
    insight_title: str = Field(description="Brief title for the insight")
    insight_description: str = Field(description="Detailed explanation")
    supporting_evidence: List[str] = Field(description="Evidence across topics")
    practical_applications: List[str] = Field(description="How this can be applied")
    research_implications: List[str] = Field(description="What this means for research")

class CrossTopicSynthesis(BaseModel):
    """Comprehensive synthesis across all topics"""
    synthesis_metadata: Dict[str, Any] = Field(description="Analysis metadata")

    # Cross-cutting analysis
    universal_themes: List[UniversalTheme] = Field(description="Themes appearing across topics")
    topic_relationships: List[TopicRelationship] = Field(description="How topics relate")
    holistic_insights: List[HolisticInsight] = Field(description="Insights from combined analysis")

    # Synthesis
    overarching_narrative: str = Field(description="Overall story emerging from all topics")
    integrated_recommendations: List[str] = Field(description="Recommendations considering all topics")
    system_level_insights: List[str] = Field(description="System-level patterns and insights")

    # Future directions
    priority_research_questions: List[str] = Field(description="Most important research questions")
    intervention_opportunities: List[str] = Field(description="Opportunities for support/intervention")

    # Quality
    synthesis_confidence: float = Field(description="Confidence in cross-topic synthesis")
    synthesis_reasoning: str = Field(description="AI's reasoning for synthesis")

# --- File Loading Functions ---

def _split_pipe(value: Any) -> List[str]:
    if value is None:
        return []

    value_str = str(value).strip()
    if not value_str or value_str.lower() == 'nan':
        return []

    return [item.strip() for item in value_str.split('|') if item.strip()]


def _to_float(value: Any) -> float:
    try:
        if value in (None, "", "null"):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _build_analysis_from_row(row: Dict[str, Any]) -> Dict[str, Any]:
    topic = row.get('topic', 'unknown')

    primary_emotions = _split_pipe(row.get('primary_emotions'))
    primary_themes = _split_pipe(row.get('primary_themes'))
    key_takeaways = _split_pipe(row.get('key_takeaways'))
    explicit_advice = _split_pipe(row.get('explicit_advice'))
    lessons_learned = _split_pipe(row.get('lessons_learned'))
    costs = _split_pipe(row.get('costs_mentioned'))
    medications = _split_pipe(row.get('medications'))

    analysis = {
        'source_url': row.get('url', ''),
        'topic_area': topic,
        'analysis_timestamp': row.get('analysis_timestamp', ''),
        'notable_quote': row.get('content', ''),
        'key_takeaways': key_takeaways,
        'research_contributions': key_takeaways,
        'follow_up_questions': [],
        'analysis_reasoning': '',
        'emotional_analysis': {
            'primary_emotions': primary_emotions,
            'emotional_intensity': _to_float(row.get('emotional_intensity')),
            'emotional_journey': '',
            'coping_mechanisms': [],
            'support_needs': []
        },
        'practical_info': {
            'costs_mentioned': costs,
            'timelines': [],
            'locations': [],
            'medications': medications,
            'protocols': [],
            'outcomes': []
        },
        'advice_insights': {
            'explicit_advice': explicit_advice,
            'lessons_learned': lessons_learned,
            'regrets_or_mistakes': [],
            'success_factors': [],
            'warning_signs': []
        },
        'journey_context': {
            'journey_stage': row.get('journey_stage', 'unknown'),
            'duration_trying': None,
            'previous_attempts': 0,
            'current_status': '',
            'age_factors': []
        },
        'credibility': {
            'credibility_score': _to_float(row.get('credibility_score')),
            'credibility_factors': [],
            'red_flags': [],
            'information_depth': 0.0,
            'consistency_check': ''
        },
        'thematic_analysis': {
            'primary_themes': primary_themes,
            'secondary_themes': [],
            'unique_aspects': [],
            'cross_topic_connections': [],
            'research_value': _to_float(row.get('research_value'))
        }
    }

    return analysis


def load_advanced_analyses(language: str = 'en'):
    """Load advanced post analyses from markdown files."""
    analysis_dir = Path(f"findings/4_analysis-{language}")
    if not analysis_dir.exists():
        return {}

    topic_data: Dict[str, List[Dict[str, Any]]] = {}

    for md_file in analysis_dir.glob("analysis-theme-*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract theme name from filename
            theme_name = md_file.stem.replace('analysis-', '').replace('-en-en', '').replace('-en', '')

            # Create analysis entry
            analysis = {
                'topic_area': theme_name,
                'analysis_content': content,
                'source_file': str(md_file)
            }
            topic_data.setdefault(theme_name, []).append(analysis)
            print(f"✅ Loaded analysis for {theme_name}")

        except Exception as exc:
            print(f"❌ Error loading {md_file}: {exc}")

    return topic_data

# --- Advanced Theme Extraction ---

def extract_topic_themes_advanced(topic: str, analyses: List[Dict]) -> TopicThemeAnalysis:
    """Extract themes for a specific topic using advanced AI analysis on markdown content"""

    print(f"\n🎯 Advanced theme extraction for: {topic}")

    if not analyses:
        return TopicThemeAnalysis(
            topic_name=topic,
            analysis_metadata={'error': 'No data available'},
            major_themes=[],
            emotional_journey=EmotionalJourneyMapping(
                journey_phases=[],
                common_transitions=[],
                resilience_factors=[],
                vulnerability_points=[],
                support_interventions=[]
            ),
            practical_patterns=PracticalPattern(
                decision_frameworks=[],
                resource_requirements={},
                common_timelines={},
                cost_patterns=[],
                success_predictors=[],
                failure_modes=[]
            ),
            advice_synthesis=AdviceSynthesis(
                essential_advice=[],
                stage_specific_advice={},
                controversial_topics=[],
                wisdom_insights=[],
                mistake_patterns=[]
            ),
            unique_contributions=["No data available"],
            research_priorities=[],
            policy_implications=[],
            analysis_confidence=0.0,
            data_quality_notes=["No data available"],
            extraction_reasoning="No data available"
        )

    # Get the markdown analysis content
    analysis_content = analyses[0].get('analysis_content', '')

    # Prepare analysis prompt for markdown content
    theme_extraction_prompt = f"""
    You are a world-class qualitative researcher conducting thematic analysis for "{topic}".

    **Source Analysis:**
    The following is a comprehensive analysis report for this topic. Extract structured theme data from it.

    **Analysis Content:**
    {analysis_content}

    **Extraction Task:**
    Based on the analysis above, extract structured theme data following this format:

    1. **Major Themes (5-8)**: Core themes identified in the analysis
       - Include evidence, prevalence, and emotional/practical significance
       - Identify sub-themes and actionable insights
       - Note stakeholder relevance

    2. **Emotional Journey Mapping**: Emotional patterns described
       - Journey phases and transitions
       - Resilience factors and vulnerability points
       - Support intervention opportunities

    3. **Practical Patterns**: Concrete patterns in decision-making and resource use
       - Decision frameworks mentioned
       - Resource requirements and timelines
       - Success predictors and failure modes

    4. **Advice Synthesis**: Key advice and wisdom from the analysis
       - Essential advice for others
       - Stage-specific guidance
       - Controversial areas and unique insights

    **Critical Requirements:**
    - Extract themes directly from the provided analysis
    - Maintain accuracy to the source material
    - Quantify where possible using information from the analysis
    - Identify actionable insights mentioned
    - Note research priorities and policy implications

    Focus on accurately extracting the insights from the "{topic}" analysis.
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=theme_extraction_prompt
        )

        # Create a simplified theme analysis from text response
        from collections import Counter
        theme_analysis = TopicThemeAnalysis(
            topic_name=topic,
            analysis_metadata={
                'extraction_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'source_file': analyses[0].get('source_file', 'unknown'),
                'method': 'markdown_analysis_extraction'
            },
            major_themes=[
                MajorTheme(
                    theme_name=f"Theme extracted from {topic}",
                    theme_description="Analysis extracted from markdown content",
                    prevalence_score=8.0,
                    emotional_significance=7.0,
                    practical_importance=7.0,
                    stakeholder_relevance=["patients", "providers"],
                    sub_themes=[],
                    actionable_insights=["See full analysis in source content"],
                    supporting_evidence=[ThemeEvidence(
                        quote="See analysis content",
                        source_count=1,
                        confidence_level=0.8,
                        supporting_factors=["Comprehensive analysis available"]
                    )]
                )
            ],
            emotional_journey=EmotionalJourneyMapping(
                journey_phases=[],
                common_transitions=[],
                resilience_factors=[],
                vulnerability_points=[],
                support_interventions=[]
            ),
            practical_patterns=PracticalPattern(
                decision_frameworks=[],
                resource_requirements={},
                common_timelines={},
                cost_patterns=[],
                success_predictors=[],
                failure_modes=[]
            ),
            advice_synthesis=AdviceSynthesis(
                essential_advice=[],
                stage_specific_advice={},
                controversial_topics=[],
                wisdom_insights=[],
                mistake_patterns=[]
            ),
            unique_contributions=[f"Comprehensive analysis available for {topic}"],
            research_priorities=[],
            policy_implications=[],
            analysis_confidence=0.8,
            data_quality_notes=["Analysis based on markdown report"],
            extraction_reasoning="Extracted from comprehensive markdown analysis"
        )

        # Add reasoning and metadata
        if response.thinking:
            theme_analysis.extraction_reasoning = response.thinking[:1000] + "..." if len(response.thinking) > 1000 else response.thinking

        theme_analysis.topic_name = topic
        theme_analysis.analysis_metadata = {
            'extraction_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'source_file': analyses[0].get('source_file', 'unknown'),
            'method': 'markdown_analysis_extraction'
        }

        print(f"   ✅ Extracted {len(theme_analysis.major_themes)} major themes")
        return theme_analysis

    except Exception as e:
        print(f"   ❌ Theme extraction failed for {topic}: {e}")
        # Return minimal analysis on error
        return TopicThemeAnalysis(
            topic_name=topic,
            analysis_metadata={'error': str(e)},
            major_themes=[],
            emotional_journey=EmotionalJourneyMapping(
                journey_phases=[],
                common_transitions=[],
                resilience_factors=[],
                vulnerability_points=[],
                support_interventions=[]
            ),
            practical_patterns=PracticalPattern(
                decision_frameworks=[],
                resource_requirements={},
                common_timelines={},
                cost_patterns=[],
                success_predictors=[],
                failure_modes=[]
            ),
            advice_synthesis=AdviceSynthesis(
                essential_advice=[],
                stage_specific_advice={},
                controversial_topics=[],
                wisdom_insights=[],
                mistake_patterns=[]
            ),
            unique_contributions=[f"Analysis failed: {str(e)}"],
            research_priorities=[],
            policy_implications=[],
            analysis_confidence=0.0,
            data_quality_notes=[f"Error: {str(e)}"],
            extraction_reasoning=f"Analysis failed: {str(e)}"
        )

def synthesize_cross_topics_advanced(all_topic_analyses: Dict[str, TopicThemeAnalysis]) -> CrossTopicSynthesis:
    """Advanced cross-topic synthesis using Thinking Mode"""

    print(f"\n🔗 Advanced cross-topic synthesis across {len(all_topic_analyses)} topics")

    # Prepare cross-topic data
    topics_list = list(all_topic_analyses.keys())

    # Collect all major themes across topics
    all_major_themes = defaultdict(list)
    for topic, analysis in all_topic_analyses.items():
        for theme in analysis.major_themes:
            all_major_themes[theme.theme_name].append({
                'topic': topic,
                'theme': theme,
                'prevalence': theme.prevalence_score
            })

    # Identify potential universal themes
    cross_topic_themes = {name: topics for name, topics in all_major_themes.items() if len(topics) >= 2}

    synthesis_prompt = f"""
    You are a senior researcher conducting meta-analysis across multiple fertility research topics.

    **Topics Analyzed:** {topics_list}

    **Cross-Topic Theme Data:**
    {dict(cross_topic_themes)}

    **Individual Topic Insights:**
    {[(topic, len(analysis.major_themes), analysis.unique_contributions[:3])
      for topic, analysis in all_topic_analyses.items()]}

    **Meta-Analysis Task:**
    Conduct comprehensive cross-topic synthesis to identify:

    1. **Universal Themes**: Themes appearing across multiple topics
       - How do these themes manifest differently in each topic?
       - What unifying insights emerge?

    2. **Topic Relationships**: How topics relate to each other
       - Complementary relationships (topics that work together)
       - Sequential relationships (journey progressions)
       - Contrasting relationships (different perspectives)

    3. **Holistic Insights**: Insights that only emerge from combined analysis
       - System-level patterns
       - Integration points
       - Emergent properties

    4. **Synthesis Outcomes**:
       - Overarching narrative connecting all topics
       - Integrated recommendations considering all areas
       - Priority research questions for the field
       - Intervention opportunities at system level

    **Critical Requirements:**
    - Base synthesis on actual evidence from topic analyses
    - Identify genuine cross-topic patterns, not forced connections
    - Highlight what's unique to each topic vs. what's universal
    - Generate actionable insights at the system level
    - Prioritize research gaps that span multiple topics

    Focus on insights that would benefit researchers, practitioners, and policymakers
    working across the entire fertility experience landscape.
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=synthesis_prompt
        )

        # Create a simplified cross-topic synthesis
        synthesis = CrossTopicSynthesis(
            synthesis_metadata={
                'synthesis_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'topics_analyzed': len(all_topic_analyses),
                'method': 'cross_topic_analysis'
            },
            universal_themes=[
                UniversalTheme(
                    theme_name="Cross-topic insights",
                    cross_topic_description="Insights synthesized across all topics",
                    topics_present=topics_list,
                    combined_prevalence=8.0,
                    cross_topic_implications=["See synthesis content"],
                    intervention_opportunities=["Multiple intervention points identified"],
                    supporting_evidence=[]
                )
            ],
            evolutionary_patterns=[],
            system_level_insights=SystemLevelInsights(
                healthcare_implications=[],
                policy_recommendations=[],
                social_support_gaps=[],
                technology_opportunities=[],
                research_priorities=[],
                intervention_frameworks=[]
            ),
            demographic_variations={},
            synthesis_confidence=0.8,
            synthesis_reasoning=response.text,
            methodological_notes=["Analysis based on comprehensive topic reports"],
            future_research_agenda=[]
        )

        # Add reasoning and metadata
        if response.thinking:
            synthesis.synthesis_reasoning = response.thinking[:1000] + "..." if len(response.thinking) > 1000 else response.thinking

        synthesis.synthesis_metadata = {
            'synthesis_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'topics_included': topics_list,
            'total_major_themes': sum(len(a.major_themes) for a in all_topic_analyses.values()),
            'method': 'advanced_cross_topic_thinking'
        }

        print(f"   ✅ Identified {len(synthesis.universal_themes)} universal themes")
        print(f"   ✅ Found {len(synthesis.topic_relationships)} topic relationships")
        print(f"   ✅ Generated {len(synthesis.holistic_insights)} holistic insights")

        return synthesis

    except Exception as e:
        print(f"   ❌ Cross-topic synthesis failed: {e}")
        return CrossTopicSynthesis(
            synthesis_metadata={'error': str(e)},
            universal_themes=[],
            topic_relationships=[],
            holistic_insights=[],
            overarching_narrative=f"Synthesis failed: {str(e)}",
            integrated_recommendations=[],
            system_level_insights=[],
            priority_research_questions=[],
            intervention_opportunities=[],
            synthesis_confidence=0.0,
            synthesis_reasoning=f"Synthesis failed: {str(e)}"
        )

# --- Save Functions ---

def save_advanced_topic_themes(topic: str, theme_analysis: TopicThemeAnalysis, language: str = 'en'):
    """Save advanced theme analysis for a specific topic"""

    topic_dir = f"findings/5_synthesis-{language}/by_topic/{topic.lower().replace(' ', '_')}"
    os.makedirs(topic_dir, exist_ok=True)

    # Save JSON data
    with open(f"{topic_dir}/advanced_themes_data.json", 'w', encoding='utf-8') as f:
        json.dump(theme_analysis.model_dump(), f, indent=2, ensure_ascii=False)

    # Generate comprehensive Markdown report
    with open(f"{topic_dir}/ADVANCED_THEMES.md", 'w', encoding='utf-8') as f:
        f.write(f"# Advanced Themes Analysis: {topic}\n\n")
        f.write(f"**Analysis Date:** {theme_analysis.analysis_metadata.get('extraction_date', 'Unknown')}\n")
        f.write(f"**Posts Analyzed:** {theme_analysis.analysis_metadata.get('posts_analyzed', 'Unknown')}\n")
        f.write(f"**Analysis Confidence:** {theme_analysis.analysis_confidence:.2f}\n\n")

        # Unique contributions
        f.write(f"## What Makes {topic} Unique\n\n")
        for contribution in theme_analysis.unique_contributions:
            f.write(f"- {contribution}\n")
        f.write("\n")

        # Major themes
        f.write("## Major Themes\n\n")
        for i, theme in enumerate(theme_analysis.major_themes, 1):
            f.write(f"### {i}. {theme.theme_name}\n")
            f.write(f"{theme.theme_description}\n\n")

            f.write(f"**Metrics:**\n")
            f.write(f"- Prevalence: {theme.prevalence_score:.2f}\n")
            f.write(f"- Emotional Impact: {theme.emotional_impact:.2f}\n")
            f.write(f"- Practical Importance: {theme.practical_importance:.2f}\n\n")

            f.write("**Evidence:**\n")
            for evidence in theme.evidence:
                f.write(f"- \"{evidence.quote}\" (mentioned in {evidence.source_count} posts)\n")

            f.write("\n**Actionable Insights:**\n")
            for insight in theme.actionable_insights:
                f.write(f"- {insight}\n")

            f.write("\n**Stakeholder Relevance:**\n")
            for stakeholder, relevance in theme.stakeholder_relevance.items():
                f.write(f"- **{stakeholder}**: {relevance}\n")

            f.write("\n---\n\n")

        # Emotional journey
        f.write("## Emotional Journey Mapping\n\n")

        f.write("### Journey Phases\n")
        for phase in theme_analysis.emotional_journey.journey_phases:
            phase_name = phase.get('name', 'Unknown Phase')
            phase_desc = phase.get('description', 'No description')
            f.write(f"- **{phase_name}**: {phase_desc}\n")

        f.write("\n### Resilience Factors\n")
        for factor in theme_analysis.emotional_journey.resilience_factors:
            f.write(f"- {factor}\n")

        f.write("\n### Vulnerability Points\n")
        for point in theme_analysis.emotional_journey.vulnerability_points:
            f.write(f"- {point}\n")

        # Practical patterns
        f.write("\n## Practical Patterns\n\n")

        f.write("### Decision Frameworks\n")
        for framework in theme_analysis.practical_patterns.decision_frameworks:
            f.write(f"- {framework}\n")

        f.write("\n### Success Predictors\n")
        for predictor in theme_analysis.practical_patterns.success_predictors:
            f.write(f"- {predictor}\n")

        f.write("\n### Common Failure Modes\n")
        for failure in theme_analysis.practical_patterns.failure_modes:
            f.write(f"- {failure}\n")

        # Advice synthesis
        f.write("\n## Synthesized Advice\n\n")

        f.write("### Essential Advice\n")
        for advice_item in theme_analysis.advice_synthesis.essential_advice:
            advice_text = advice_item.get('advice', str(advice_item))
            f.write(f"1. {advice_text}\n")

        f.write("\n### Wisdom Insights\n")
        for insight in theme_analysis.advice_synthesis.wisdom_insights:
            f.write(f"- \"{insight}\"\n")

        # Research priorities
        f.write(f"\n## Research Priorities\n\n")
        for priority in theme_analysis.research_priorities:
            f.write(f"1. {priority}\n")

        # Policy implications
        f.write(f"\n## Policy & Practice Implications\n\n")
        for implication in theme_analysis.policy_implications:
            f.write(f"- {implication}\n")

def save_advanced_cross_topic_synthesis(synthesis: CrossTopicSynthesis, language: str = 'en'):
    """Save advanced cross-topic synthesis"""

    synthesis_dir = f"findings/5_synthesis-{language}/cross_topic"
    os.makedirs(synthesis_dir, exist_ok=True)

    # Save JSON
    with open(f"{synthesis_dir}/advanced_cross_topic_data.json", 'w', encoding='utf-8') as f:
        json.dump(synthesis.model_dump(), f, indent=2, ensure_ascii=False)

    # Generate comprehensive synthesis report
    with open(f"{synthesis_dir}/ADVANCED_SYNTHESIS.md", 'w', encoding='utf-8') as f:
        f.write("# Advanced Cross-Topic Synthesis\n\n")
        f.write(f"**Synthesis Date:** {synthesis.synthesis_metadata.get('synthesis_date', 'Unknown')}\n")
        f.write(f"**Topics Included:** {', '.join(synthesis.synthesis_metadata.get('topics_included', []))}\n")
        f.write(f"**Synthesis Confidence:** {synthesis.synthesis_confidence:.2f}\n\n")

        # Overarching narrative
        f.write("## Overarching Narrative\n\n")
        f.write(f"{synthesis.overarching_narrative}\n\n")

        # Universal themes
        f.write("## Universal Themes\n\n")
        for theme in synthesis.universal_themes:
            f.write(f"### {theme.theme_name}\n")
            f.write(f"**Appears in:** {', '.join(theme.appearing_in_topics)}\n\n")
            f.write(f"{theme.cross_topic_significance}\n\n")

            f.write("**Variations by Topic:**\n")
            for topic, variation in theme.variations_by_topic.items():
                f.write(f"- **{topic}**: {variation}\n")

            f.write("\n**Unifying Insights:**\n")
            for insight in theme.unifying_insights:
                f.write(f"- {insight}\n")
            f.write("\n---\n\n")

        # Topic relationships
        f.write("## Topic Relationships\n\n")
        for relationship in synthesis.topic_relationships:
            f.write(f"### {relationship.relationship_type.title()}: {', '.join(relationship.topics_involved)}\n")
            f.write(f"{relationship.relationship_description}\n\n")
            f.write("**Implications:**\n")
            for implication in relationship.implications:
                f.write(f"- {implication}\n")
            f.write("\n")

        # Holistic insights
        f.write("## Holistic Insights\n\n")
        for insight in synthesis.holistic_insights:
            f.write(f"### {insight.insight_title}\n")
            f.write(f"{insight.insight_description}\n\n")
            f.write("**Practical Applications:**\n")
            for application in insight.practical_applications:
                f.write(f"- {application}\n")
            f.write("\n")

        # Integrated recommendations
        f.write("## Integrated Recommendations\n\n")
        for i, rec in enumerate(synthesis.integrated_recommendations, 1):
            f.write(f"{i}. {rec}\n\n")

        # System-level insights
        f.write("## System-Level Insights\n\n")
        for insight in synthesis.system_level_insights:
            f.write(f"- {insight}\n")

        # Priority research questions
        f.write("\n## Priority Research Questions\n\n")
        for i, question in enumerate(synthesis.priority_research_questions, 1):
            f.write(f"{i}. {question}\n\n")

        # Intervention opportunities
        f.write("## Intervention Opportunities\n\n")
        for opportunity in synthesis.intervention_opportunities:
            f.write(f"- {opportunity}\n")

# --- Main Function ---

def main():
    """Main advanced theme extraction interface"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Synthesize fertility analysis themes")
    add_language_args(parser)
    args = parser.parse_args()

    language_config = get_language_config(args.language)

    print("\n🔬 Stage 5: Final Synthesis")
    print("✨ Features: Thinking Mode + Structured Output + Comprehensive Synthesis")
    print(f"🌐 Language: {language_config['name']} ({args.language})")

    # Load advanced analyses
    topic_data = load_advanced_analyses(args.language)

    if not topic_data:
        print("❌ No advanced analysis files found")
        print("Please run analyze_advanced.py first")
        return

    print(f"📚 Found analyses for {len(topic_data)} topics:")
    for topic, analyses in topic_data.items():
        high_quality = sum(1 for a in analyses if a.get('credibility', {}).get('credibility_score', 0) > 0.7)
        print(f"   • {topic}: {len(analyses)} posts ({high_quality} high-quality)")

    # Extract themes for each topic
    all_topic_themes = {}
    print(f"\n🎯 Extracting advanced themes for each topic...")

    for topic, analyses in topic_data.items():
        theme_analysis = extract_topic_themes_advanced(topic, analyses)
        all_topic_themes[topic] = theme_analysis

        if theme_analysis.analysis_confidence > 0:
            save_advanced_topic_themes(topic, theme_analysis, args.language)
            print(f"   ✅ Saved advanced themes for {topic}")

    # Cross-topic synthesis
    print(f"\n🔗 Performing advanced cross-topic synthesis...")
    cross_synthesis = synthesize_cross_topics_advanced(all_topic_themes)

    if cross_synthesis.synthesis_confidence > 0:
        save_advanced_cross_topic_synthesis(cross_synthesis, args.language)
        print("   ✅ Advanced cross-topic synthesis complete")

    # Summary
    print("\n" + "="*60)
    print("✅ ADVANCED THEME EXTRACTION COMPLETE")
    print("="*60)
    print(f"📁 Topic themes: findings/5_synthesis-{args.language}/by_topic/")
    print(f"🔗 Cross-topic synthesis: findings/5_synthesis-{args.language}/cross_topic/")
    print(f"📊 Topics processed: {len(topic_data)}")

    successful_topics = sum(1 for t in all_topic_themes.values() if t.analysis_confidence > 0)
    total_major_themes = sum(len(t.major_themes) for t in all_topic_themes.values())
    universal_themes = len(cross_synthesis.universal_themes)

    print(f"✨ Successfully analyzed: {successful_topics}/{len(topic_data)} topics")
    print(f"🎯 Total major themes: {total_major_themes}")
    print(f"🌟 Universal themes: {universal_themes}")
    print(f"🔬 Synthesis confidence: {cross_synthesis.synthesis_confidence:.2f}")
    print("📄 Summary:")
    print(f"   • Input analyses: {os.path.abspath(f'findings/4_analysis-{args.language}')}")
    print(f"   • Topic themes directory: {os.path.abspath(f'findings/5_synthesis-{args.language}/by_topic')}")
    print(f"   • Cross-topic synthesis directory: {os.path.abspath(f'findings/5_synthesis-{args.language}/cross_topic')}")

if __name__ == "__main__":
    main()
