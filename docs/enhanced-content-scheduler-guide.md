# Enhanced Content Scheduler Guide

## Overview

The Enhanced Content Scheduler is a comprehensive automation system that generates viral content for multiple social media channels with built-in quality checks and performance tracking. It ensures that only high-quality content with viral potential above 0.7 is approved for distribution.

## Key Features

### 🎯 Quality Control System
- **Viral Potential Threshold**: Content must have viral potential > 0.7 to be approved
- **AI-Powered Assessment**: Uses Ollama for intelligent quality evaluation
- **Multi-Factor Scoring**: Combines viral potential, engagement likelihood, and adaptation quality
- **Automatic Regeneration**: Rejects low-quality content and regenerates with higher focus

### 📊 Performance Tracking
- **Mock Views Generation**: Realistic view counts based on channel and viral potential
- **Engagement Rate Calculation**: Channel-specific engagement rate predictions
- **Revenue Estimation**: Mock revenue calculations based on views and engagement
- **CSV Analytics**: Persistent tracking of all performance metrics

### 🔄 Daily Automation
- **7-Day Schedule**: Runs daily content generation for 5 channels
- **Quality Checks**: Filters content through quality assessment pipeline
- **Performance Monitoring**: Tracks daily performance with mock data updates
- **Analytics Integration**: Saves all data to local CSV files

## Architecture

### Content Flow
```
1. Generate Viral Idea → 2. Quality Check → 3. Repurpose for Channels → 4. Quality Check → 5. Performance Tracking → 6. Analytics Save
```

### Quality Assessment Pipeline
```
Content Idea → Viral Potential Check → AI Assessment → Quality Score → Approval/Rejection
```

### Performance Tracking Pipeline
```
Approved Content → Mock Views → Mock Engagement → Revenue Calculation → CSV Analytics
```

## Configuration

### Quality Threshold
```python
scheduler.quality_threshold = 0.7  # Default threshold
```

### Channel-Specific Settings
Each channel has optimized configurations:

| Channel | View Range | Engagement Range | Optimal Length | Best Time |
|---------|------------|-----------------|----------------|-----------|
| YouTube | 1K-50K | 5-15% | 10-15 min | 15:00-17:00 |
| TikTok | 5K-100K | 8-25% | 15-60 sec | 19:00-21:00 |
| Instagram | 2K-30K | 6-18% | 30-60 sec | 12:00-14:00 |
| LinkedIn | 500-10K | 4-12% | 1-3 min | 09:00-11:00 |
| Twitter | 1K-25K | 5-15% | 2-3 min | 08:00-10:00 |

## Usage Examples

### Basic Content Generation
```python
from content_scheduler import ContentScheduler

scheduler = ContentScheduler()
await scheduler.generate_daily_content()
```

### Manual Quality Assessment
```python
from ai import ContentIdea, ContentType

test_idea = ContentIdea(
    title="Test Content",
    description="Test description",
    content_type=ContentType.VIDEO,
    target_audience="Tech professionals",
    viral_potential=0.85,
    estimated_revenue=500.0,
    keywords=["test", "viral"],
    hashtags=["#test", "#viral"]
)

quality_result = await scheduler._assess_content_quality(test_idea)
print(f"Quality Score: {quality_result['score']:.2f}")
print(f"Passed: {quality_result['passed']}")
```

### Performance Tracking
```python
# Content is automatically tracked when generated
content = await scheduler.manual_generate_content()

for item in content:
    print(f"Channel: {item.channel.value}")
    print(f"Views: {item.mock_views:,}")
    print(f"Engagement: {item.mock_engagement_rate:.2%}")
    print(f"Quality Score: {item.quality_score:.2f}")
```

## Data Structures

### RepurposedContent
```python
@dataclass
class RepurposedContent:
    original_idea: ContentIdea
    channel: ChannelType
    adapted_title: str
    adapted_description: str
    platform_specific_hooks: List[str]
    optimal_posting_time: str
    hashtags: List[str]
    content_format: str
    estimated_engagement: float
    viral_potential: float
    quality_score: float
    mock_views: int
    mock_engagement_rate: float
    created_at: datetime
```

### ContentPerformance
```python
@dataclass
class ContentPerformance:
    content_id: str
    title: str
    channel: str
    viral_potential: float
    quality_score: float
    mock_views: int
    mock_engagement_rate: float
    mock_revenue: float
    created_at: datetime
    performance_date: datetime
```

## Analytics Output

### CSV File Structure
The system creates `data/content_performance_analytics.csv` with the following columns:

| Column | Description |
|--------|-------------|
| content_id | Unique identifier for content piece |
| title | Content title |
| channel | Social media channel |
| viral_potential | Viral potential score (0-1) |
| quality_score | Overall quality score (0-1) |
| mock_views | Simulated view count |
| mock_engagement_rate | Simulated engagement rate |
| mock_revenue | Estimated revenue |
| created_at | Content creation timestamp |
| performance_date | Performance tracking timestamp |

### Sample CSV Output
```csv
content_id,title,channel,viral_potential,quality_score,mock_views,mock_engagement_rate,mock_revenue,created_at,performance_date
youtube_20250104_060000,AI Automation Trends - YouTube Version,youtube,0.85,0.82,25000,0.12,30.0,2025-01-04T06:00:00,2025-01-04T06:00:00
tiktok_20250104_060000,AI Automation Trends - TikTok Version,tiktok,0.85,0.78,75000,0.18,135.0,2025-01-04T06:00:00,2025-01-04T06:00:00
```

## Scheduler Jobs

### Daily Jobs
- **6:00 AM**: Daily content generation with quality checks
- **8:00 PM**: Daily performance tracking and analytics

### Weekly Jobs
- **Sunday 5:00 AM**: Weekly content planning
- **Saturday 7:00 AM**: Content performance analysis

## Quality Assessment Algorithm

### Viral Potential Check
```python
if content_idea.viral_potential < quality_threshold:
    return {"passed": False, "reason": "Below threshold"}
```

### AI Assessment
Uses Ollama to evaluate:
- Viral potential (0-1 scale)
- Engagement likelihood
- Shareability
- Trend relevance

### Quality Score Calculation
```python
quality_score = (viral_score * 0.4 + engagement_score * 0.4 + adaptation_score * 0.2)
```

## Performance Tracking Algorithm

### Mock Views Generation
```python
base_views = random.randint(view_range[0], view_range[1])
viral_multiplier = 1 + (viral_potential - 0.5) * 2
mock_views = int(base_views * viral_multiplier)
```

### Mock Engagement Rate
```python
base_engagement = random.uniform(engagement_range[0], engagement_range[1])
quality_multiplier = 1 + (quality_score - 0.5) * 0.5
mock_engagement_rate = min(base_engagement * quality_multiplier, 1.0)
```

### Revenue Calculation
```python
mock_revenue = mock_views * mock_engagement_rate * 0.01  # $0.01 per engagement
```

## Error Handling

### Quality Assessment Fallbacks
- If Ollama fails, falls back to viral potential check
- If JSON parsing fails, uses default quality indicators
- If network issues occur, uses cached quality scores

### Performance Tracking Fallbacks
- If calculation fails, uses default values
- If CSV write fails, logs error and continues
- If data corruption occurs, regenerates from source

## Monitoring and Logging

### Quality Check Logs
```
🔍 Assessing content quality...
✅ Content quality check passed (Score: 0.85)
⚠️ Content quality check failed: Viral potential (0.65) below threshold (0.7)
🔄 Regenerating content with higher quality focus...
```

### Performance Tracking Logs
```
📊 Tracking daily content performance...
📈 Daily Performance Summary:
   Total Views: 125,000
   Avg Engagement: 15.2%
   Estimated Revenue: $189.50
```

### Analytics Logs
```
✅ Tracked analytics for 5 content pieces
✅ Performance data saved to data/content_performance_analytics.csv
```

## Cost-Free Operation

### Local AI Processing
- Uses Ollama for all AI operations
- No external API costs
- Runs entirely on local infrastructure

### Local Data Storage
- CSV files stored locally
- No cloud storage costs
- All analytics data kept on-premises

### Minimal Dependencies
- Only requires APScheduler and httpx
- No expensive external services
- Self-contained operation

## Future Enhancements

### Planned Features
- **Real-time Analytics Dashboard**: Web-based performance monitoring
- **Advanced Quality Metrics**: More sophisticated quality assessment algorithms
- **Multi-language Support**: Content generation in multiple languages
- **A/B Testing Integration**: Test different content variations
- **Predictive Analytics**: Forecast content performance before posting

### Performance Optimizations
- **Caching System**: Cache quality assessments for similar content
- **Batch Processing**: Process multiple content pieces simultaneously
- **Parallel Generation**: Generate content for multiple channels in parallel
- **Smart Scheduling**: Optimize posting times based on historical data

## Troubleshooting

### Common Issues

#### Quality Check Failures
**Problem**: Content consistently fails quality checks
**Solution**: 
- Lower quality threshold temporarily
- Check Ollama connection
- Verify content generation prompts

#### Performance Tracking Issues
**Problem**: Mock data seems unrealistic
**Solution**:
- Adjust channel-specific view ranges
- Review engagement rate calculations
- Check for data corruption in CSV files

#### Scheduler Not Running
**Problem**: Jobs not executing as expected
**Solution**:
- Check scheduler status with `get_scheduler_status()`
- Verify cron job configurations
- Ensure proper timezone settings

### Debug Commands
```python
# Check scheduler status
status = scheduler.get_scheduler_status()
print(f"Running: {status['is_running']}")
print(f"Jobs: {len(status['jobs'])}")

# Test quality assessment
result = await scheduler._assess_content_quality(test_idea)
print(f"Quality result: {result}")

# Check CSV analytics
import pandas as pd
df = pd.read_csv('data/content_performance_analytics.csv')
print(f"Analytics rows: {len(df)}")
```

## Integration Examples

### With Existing AI Module
```python
from ai import AIModule
from content_scheduler import ContentScheduler

ai_module = AIModule()
scheduler = ContentScheduler()

# Generate content using AI module
ideas = await ai_module.generate_viral_content_ideas("AI trends", count=1)
if ideas:
    quality_result = await scheduler._assess_content_quality(ideas[0])
    if quality_result['passed']:
        print("High-quality content approved!")
```

### With Analytics Module
```python
from analytics import AnalyticsManager

analytics = AnalyticsManager()
scheduler = ContentScheduler()

# Track content performance
content = await scheduler.manual_generate_content()
for item in content:
    analytics.track_user_metric(
        user_id=f"content_{item.channel.value}",
        session_duration=item.mock_views / 1000,  # Mock session duration
        page_views=item.mock_views,
        conversion_rate=item.mock_engagement_rate,
        revenue=item.mock_views * item.mock_engagement_rate * 0.01
    )
```

This enhanced content scheduler provides a robust, cost-free solution for automated content generation with quality assurance and performance tracking, ensuring that only the best content reaches your audience across all social media channels. 