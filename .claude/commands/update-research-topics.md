# Update Research Topics from Discovery Data

Analyze discovery research data and update RESEARCH_TOPICS.md with new insights and refined topics.

## Usage
```
/update-research-topics
```

## What this command does

1. **Reads discovery data** from `findings/discovery/discovery.csv`
2. **Analyzes themes** emerging from the discovery research
3. **Identifies gaps** in current RESEARCH_TOPICS.md
4. **Updates RESEARCH_TOPICS.md** with:
   - New topics discovered from organic community discussions
   - Refined queries based on actual community language
   - Better duration estimates based on topic complexity
   - Improved topic descriptions and rationale

## Discovery Data Analysis

The command will:
- Count frequency of themes in discovery data
- Identify high-value content patterns (research_value >= 4)
- Extract authentic community language for queries
- Map emotional journeys across different topics
- Find gaps in current topic coverage

## Output

- **Enhanced RESEARCH_TOPICS.md** with evidence-based improvements
- **Summary report** of changes made and rationale
- **New topics added** based on discovery insights
- **Query refinements** using authentic community language

## Use Cases

- After running discovery research to capture new insights
- When you want to refine research topics based on real data
- To ensure your structured research covers all important themes
- Before running comprehensive data collection campaigns

## Note

This command uses the discovery data to make RESEARCH_TOPICS.md more comprehensive and evidence-based, ensuring your research captures genuine user needs and pain points.