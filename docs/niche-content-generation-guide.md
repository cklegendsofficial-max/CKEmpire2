# Niche Content Generation Guide

## Overview

The Niche Content Generation feature provides automated generation of content ideas specifically tailored to different niches/topics, with educational, viral, and lifestyle variations. This feature is integrated with the content scheduler for daily production and ensures cost-free operation using local AI.

## Features

### 🎯 Core Functionality
- **Niche-Specific Content**: Generate content ideas for specific niches/topics
- **Multiple Variations**: Educational, viral, and lifestyle content variations
- **2025 Trends Integration**: Incorporates current trends in content generation
- **Daily Automation**: Integrated with content scheduler for continuous production
- **Cost-Free Operation**: Uses local Ollama AI with fallback mechanisms
- **Analytics Tracking**: CSV-based tracking of niche content performance

### 📊 Content Variations
1. **Educational Content**: Tutorials, guides, and informative content
2. **Viral Content**: High-engagement, shareable content with viral potential
3. **Lifestyle Content**: Personal stories, day-in-the-life content, and experiences

### 🎨 2025 Trends Included
- AI-powered personalization
- Short-form video dominance
- Authentic storytelling
- Community-driven content
- Educational entertainment
- Sustainability focus
- Mental health awareness
- Remote work lifestyle
- Digital nomad culture
- Micro-influencer partnerships

## Architecture

### AI Module Integration
The feature is implemented in `ai.py` with the following key methods:

```python
async def generate_niche_content_ideas(niche: str, channels: int = 5) -> List[ContentIdea]
```

### Scheduler Integration
Integrated with `content_scheduler.py` for daily automation:

```python
async def _generate_daily_niche_content() -> Optional[Dict[str, Any]]
```

### Analytics Tracking
CSV-based tracking to `data/niche_content_analytics.csv`:

```python
async def _track_niche_content_analytics(niche: str, content_ideas: List[ContentIdea])
```

## Configuration

### Popular Niches (2025)
The system includes 15 popular niches for 2025:

1. AI and automation
2. Sustainable living
3. Digital nomad lifestyle
4. Mental health and wellness
5. Cryptocurrency and blockchain
6. Remote work productivity
7. Personal finance
8. Fitness and nutrition
9. Travel and adventure
10. Technology reviews
11. Business and entrepreneurship
12. Creative arts and design
13. Education and learning
14. Environmental sustainability
15. Social media marketing

### Content Generation Parameters
- **Default channels**: 5 content variations per niche
- **Variation types**: Educational, viral, lifestyle (rotating)
- **Viral potential range**: 0.6 - 1.0
- **Revenue estimation**: $30 - $70 per content piece
- **Quality threshold**: 0.7 minimum viral potential

## Usage Examples

### Basic Usage
```python
from ai import AIModule

ai_module = AIModule()

# Generate niche content ideas
content_ideas = await ai_module.generate_niche_content_ideas("AI and automation", channels=5)
```

### Scheduler Integration
```python
from content_scheduler import ContentScheduler

scheduler = ContentScheduler()

# Daily niche content generation (automated)
result = await scheduler._generate_daily_niche_content()
```

### Manual Testing
```bash
python scripts/test_niche_content_generation.py
```

## Data Structures

### ContentIdea Object
```python
@dataclass
class ContentIdea:
    title: str
    description: str
    content_type: ContentType
    target_audience: str
    viral_potential: float
    estimated_revenue: float
    keywords: List[str]
    hashtags: List[str]
    ai_generated: bool = True
    created_at: datetime = None
```

### Analytics Data Structure
```python
{
    "niche": str,
    "total_ideas": int,
    "variation_types": Dict[str, int],
    "average_viral_potential": float,
    "total_estimated_revenue": float,
    "content_types": Dict[str, int],
    "generated_at": str
}
```

## Analytics Output

### CSV File: `data/niche_content_analytics.csv`
Headers:
- Date
- Niche
- Total_Ideas
- Average_Viral_Potential
- Total_Estimated_Revenue
- Variation_Types
- Content_Types

### Sample Analytics Entry
```
2025-08-04T08:31:52.093249,Sustainable living,3,0.70,120.0,"{'educational': 2, 'lifestyle': 1}","{'video': 3}"
```

## Scheduler Jobs

### Daily Niche Content Generation
- **Schedule**: Daily at 9:00 AM
- **Function**: `_generate_daily_niche_content()`
- **Output**: 5 content ideas for a randomly selected niche
- **Analytics**: Automatic CSV tracking

### Integration with Main Content Generation
The niche content generation is integrated into the main daily content generation process:

1. Generate viral content ideas
2. Quality assessment and filtering
3. Channel repurposing
4. Business idea generation
5. Channel suggestions
6. **Niche content generation** (NEW)
7. Monetization forecasting
8. Performance tracking

## AI Integration

### Ollama Integration
- **Model**: llama3.2
- **Endpoint**: http://localhost:11434/api/generate
- **Prompt Enhancement**: Includes 2025 trends and niche-specific context
- **Fallback**: Mock content generation when Ollama is unavailable

### Prompt Structure
```python
prompt = f"""
Generate a {variation_type} content idea for the niche: "{niche}"

Requirements:
- Content type: {variation_type}
- Niche: {niche}
- Must be engaging and shareable
- Include 2025 trends: {', '.join(trends_2025[:5])}
- Target audience: {niche} enthusiasts and general audience
- Viral potential: High
- Revenue potential: Medium to High

Format the response as JSON:
{{
    "title": "Engaging title",
    "description": "Detailed description",
    "content_type": "video|article|social_media|podcast",
    "target_audience": "Specific audience",
    "viral_potential": 0.0-1.0,
    "estimated_revenue": 0.0,
    "keywords": ["keyword1", "keyword2"],
    "hashtags": ["#hashtag1", "#hashtag2"],
    "variation_type": "{variation_type}",
    "niche_focus": "{niche}",
    "trends_included": ["trend1", "trend2"]
}}
"""
```

## Mock Content Templates

### Educational Content
- **Titles**: "Complete Guide to {niche} in 2025", "5 Essential {niche} Tips Everyone Should Know"
- **Descriptions**: "Learn everything about {niche} with this comprehensive guide"
- **Focus**: Tutorials, guides, educational content

### Viral Content
- **Titles**: "Mind-Blowing {niche} Hack That Went Viral", "The {niche} Secret Nobody Talks About"
- **Descriptions**: "Viral {niche} content that will amaze your audience"
- **Focus**: High-engagement, shareable content

### Lifestyle Content
- **Titles**: "My {niche} Journey: A Day in the Life", "How {niche} Changed My Life Forever"
- **Descriptions**: "Personal story about embracing the {niche} lifestyle"
- **Focus**: Personal stories, experiences, day-in-the-life content

## Error Handling

### Ollama Connection Failures
- **Detection**: Connection timeout or server unavailable
- **Fallback**: Mock content generation with realistic templates
- **Logging**: Error messages with fallback notifications

### Content Parsing Failures
- **Detection**: Invalid JSON or missing required fields
- **Fallback**: Default content creation with niche-specific templates
- **Logging**: Warning messages with parsing details

### Analytics Tracking Failures
- **Detection**: File system errors or CSV writing issues
- **Fallback**: In-memory tracking with retry mechanisms
- **Logging**: Error messages with file path details

## Performance Metrics

### Content Quality Metrics
- **Viral Potential**: 0.6 - 1.0 range
- **Revenue Estimation**: $30 - $70 per content piece
- **Engagement Prediction**: Based on content type and variation

### Analytics Metrics
- **Total Ideas Generated**: Count of successful content ideas
- **Average Viral Potential**: Mean viral potential across all ideas
- **Total Estimated Revenue**: Sum of revenue estimates
- **Variation Distribution**: Count of each variation type

## Cost-Free Operation

### Local AI Integration
- **Ollama**: Local large language model
- **No API Costs**: All processing done locally
- **Offline Capability**: Mock content generation when offline

### Resource Optimization
- **Efficient Prompts**: Optimized for local model performance
- **Fallback Mechanisms**: Multiple layers of fallback
- **Minimal Dependencies**: Lightweight implementation

## Future Enhancements

### Planned Features
1. **Multi-Niche Generation**: Generate content for multiple niches simultaneously
2. **Trend Analysis**: Real-time trend detection and integration
3. **Performance Optimization**: Enhanced viral potential prediction
4. **Content Templates**: Expanded template library for different niches
5. **A/B Testing**: Content variation testing capabilities

### Potential Integrations
1. **Social Media APIs**: Direct posting to platforms
2. **Content Calendar**: Advanced scheduling and planning
3. **Audience Analytics**: Detailed audience insights
4. **Revenue Tracking**: Real revenue monitoring
5. **Collaboration Tools**: Team-based content creation

## Troubleshooting

### Common Issues

#### Ollama Not Running
**Symptoms**: "All connection attempts failed" errors
**Solution**: Start Ollama server or use mock content fallback
**Command**: `ollama serve`

#### CSV File Permissions
**Symptoms**: "Permission denied" when writing analytics
**Solution**: Check file permissions or create data directory
**Command**: `mkdir -p data && chmod 755 data`

#### Content Quality Issues
**Symptoms**: Low viral potential scores
**Solution**: Adjust quality threshold or regenerate with quality focus
**Configuration**: `self.quality_threshold = 0.7`

### Debug Mode
Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Commands
```bash
# Test niche content generation
python scripts/test_niche_content_generation.py

# Test scheduler integration
python -c "import asyncio; from backend.content_scheduler import ContentScheduler; asyncio.run(ContentScheduler()._generate_daily_niche_content())"

# Check analytics file
cat data/niche_content_analytics.csv
```

## Integration Examples

### With Content Scheduler
```python
# Start scheduler with niche content generation
scheduler = ContentScheduler()
await scheduler.start_scheduler()

# Manual niche content generation
result = await scheduler._generate_daily_niche_content()
print(f"Generated {result['total_ideas']} ideas for {result['niche']}")
```

### With AI Module
```python
# Direct niche content generation
ai_module = AIModule()
ideas = await ai_module.generate_niche_content_ideas("Technology reviews", channels=3)

for idea in ideas:
    print(f"Title: {idea.title}")
    print(f"Viral Potential: {idea.viral_potential:.2f}")
    print(f"Revenue: ${idea.estimated_revenue:.2f}")
```

### Analytics Monitoring
```python
import pandas as pd

# Load analytics data
df = pd.read_csv('data/niche_content_analytics.csv')

# Analyze performance
print(f"Total niches covered: {df['Niche'].nunique()}")
print(f"Average viral potential: {df['Average_Viral_Potential'].mean():.2f}")
print(f"Total revenue generated: ${df['Total_Estimated_Revenue'].sum():.2f}")
```

## Summary

The Niche Content Generation feature provides a comprehensive solution for automated content creation across different niches with educational, viral, and lifestyle variations. It integrates seamlessly with the existing content scheduler, ensures cost-free operation through local AI, and provides detailed analytics tracking for performance monitoring.

Key benefits:
- ✅ Automated niche-specific content generation
- ✅ Multiple content variations (educational/viral/lifestyle)
- ✅ 2025 trends integration
- ✅ Daily automation through scheduler
- ✅ Cost-free local AI operation
- ✅ Comprehensive analytics tracking
- ✅ Robust error handling and fallbacks
- ✅ Easy integration and testing 