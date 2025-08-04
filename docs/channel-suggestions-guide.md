# Channel Suggestions Guide

## Overview

The Channel Suggestions feature is an enhanced addition to the CK Empire Builder that automatically suggests 5 alternative channels (YouTube, TikTok, Instagram, LinkedIn, Twitter) for content distribution with channel-specific adaptations and revenue forecasting using the finance module.

## Features

### 🚀 Core Functionality

- **5-Channel Analysis**: Analyzes content for YouTube, TikTok, Instagram, LinkedIn, and Twitter
- **Content Adaptation**: Automatically adapts content for each channel's specific requirements
- **Revenue Forecasting**: Uses finance module to calculate channel-based RPM (Revenue Per Mille)
- **Daily Generation**: Integrated with scheduler for daily content generation
- **Local AI**: Uses Ollama for cost-free AI generation

### 📊 Channel-Specific Adaptations

Each channel has unique characteristics and requirements:

#### YouTube
- **Optimal Length**: 10-15 minutes
- **Format**: Long-form video
- **RPM Range**: $2.0-$8.0 per 1000 views
- **Focus**: Educational, detailed, SEO-optimized
- **Best Time**: 15:00-17:00
- **Hashtag Limit**: 15

#### TikTok
- **Optimal Length**: 15-60 seconds
- **Format**: Short-form video
- **RPM Range**: $0.5-$2.0 per 1000 views
- **Focus**: Trending, viral, hook-based
- **Best Time**: 19:00-21:00
- **Hashtag Limit**: 5

#### Instagram
- **Optimal Length**: 30-60 seconds
- **Format**: Reel
- **RPM Range**: $1.0-$4.0 per 1000 views
- **Focus**: Visual, aesthetic, story-driven
- **Best Time**: 12:00-14:00
- **Hashtag Limit**: 30

#### LinkedIn
- **Optimal Length**: 1-3 minutes
- **Format**: Professional video
- **RPM Range**: $3.0-$10.0 per 1000 views
- **Focus**: Professional, business-focused, thought leadership
- **Best Time**: 09:00-11:00
- **Hashtag Limit**: 5

#### Twitter
- **Optimal Length**: 2-3 minutes
- **Format**: Thread
- **RPM Range**: $1.5-$5.0 per 1000 views
- **Focus**: Conversational, trending, engagement-driven
- **Best Time**: 08:00-10:00
- **Hashtag Limit**: 3

## Architecture

### Components

1. **AI Module (`ai.py`)**
   - `suggest_alternative_channels()`: Main method
   - `_generate_channel_adaptation()`: Ollama integration for content adaptation
   - `_calculate_channel_revenue_forecast()`: Finance integration for revenue forecasting
   - `_track_channel_suggestions_analytics()`: Analytics tracking

2. **Content Scheduler (`content_scheduler.py`)**
   - `_generate_channel_suggestions()`: Daily channel suggestions generation
   - Integration with existing content generation workflow

3. **Finance Module (`finance.py`)**
   - Revenue forecasting using RPM calculations
   - ROI analysis for each channel
   - Monthly and yearly projections

### Data Flow

```
Original Content → Channel Analysis → Content Adaptation → Revenue Forecast → Analytics
      ↓                ↓                    ↓                    ↓              ↓
   AI Module → 5 Channels → Ollama AI → Finance Calc → Analytics File
```

## Installation

### Prerequisites

1. **Ollama Installation**
   ```bash
   # Install Ollama (https://ollama.ai/)
   # Download and install for your platform
   
   # Pull Llama2 model
   ollama pull llama2
   ```

2. **Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. **Environment Variables**
   ```bash
   # Ollama URL (default: http://localhost:11434)
   export OLLAMA_URL="http://localhost:11434"
   ```

2. **Data Directory**
   ```bash
   # Create data directory for outputs
   mkdir -p data
   ```

## Usage

### API Endpoints

The channel suggestions are integrated into the content scheduler API:

```bash
# Start the scheduler (includes channel suggestions)
curl -X POST http://localhost:8000/api/v1/content-scheduler/start

# Check scheduler status
curl -X GET http://localhost:8000/api/v1/content-scheduler/status

# Manual content generation with channel suggestions
curl -X POST http://localhost:8000/api/v1/content-scheduler/generate-content
```

### Python Usage

```python
from ai import AIModule

# Initialize AI module
ai_module = AIModule()

# Create sample content
original_content = {
    "title": "AI Automation Trends 2025",
    "description": "Comprehensive guide to AI automation trends",
    "content_type": "video",
    "target_audience": "Tech professionals",
    "viral_potential": 0.85,
    "estimated_revenue": 500.0,
    "keywords": ["AI", "automation", "trends"],
    "hashtags": ["#AI", "#automation"]
}

# Generate channel suggestions
result = await ai_module.suggest_alternative_channels(original_content)

if result["status"] == "success":
    channel_suggestions = result["channel_suggestions"]
    total_revenue = result["total_potential_revenue"]
    
    print(f"Total potential revenue: ${total_revenue:.2f}/month")
    
    for channel, suggestion in channel_suggestions.items():
        adaptation = suggestion["adaptation"]
        revenue_forecast = suggestion["revenue_forecast"]
        
        print(f"{channel.upper()}:")
        print(f"  Title: {adaptation['adapted_title']}")
        print(f"  Revenue: ${revenue_forecast['monthly_revenue']:.2f}/month")
```

### Scheduler Integration

The channel suggestions run automatically as part of the daily content scheduler:

```python
from content_scheduler import ContentScheduler

# Initialize scheduler
scheduler = ContentScheduler()

# Start scheduler (runs daily at 6:00 AM)
await scheduler.start_scheduler()

# Channel suggestions are generated automatically
# along with viral content and business ideas
```

## Channel Suggestions Structure

### Generated Channel Suggestion Format

```json
{
    "original_content": {
        "title": "AI Automation Trends 2025",
        "description": "Comprehensive guide to AI automation trends",
        "content_type": "video"
    },
    "channel_suggestions": {
        "youtube": {
            "channel_name": "YouTube",
            "adaptation": {
                "adapted_title": "AI Automation Trends 2025 - YouTube Version",
                "adapted_description": "Comprehensive guide optimized for YouTube",
                "content_script": "Detailed 15-minute video script",
                "key_hooks": ["Start with shocking statistic", "End with call-to-action"],
                "optimal_hashtags": ["#AI", "#automation", "#trends"],
                "posting_strategy": "Post at 15:00-17:00 for maximum engagement",
                "engagement_tips": ["Use cards and end screens", "Respond to comments"],
                "estimated_views": 5000,
                "estimated_engagement_rate": 0.08
            },
            "revenue_forecast": {
                "monthly_revenue": 750.0,
                "yearly_revenue": 9000.0,
                "avg_rpm": 5.0,
                "estimated_views_per_month": 150000,
                "engagement_rate": 0.08,
                "monthly_projections": [...],
                "roi_percentage": 1500.0,
                "payback_period": 0.0
            },
            "channel_config": {
                "name": "YouTube",
                "optimal_length": "10-15 minutes",
                "format": "video",
                "rpm_range": [2.0, 8.0],
                "engagement_rate": 0.08
            }
        }
    },
    "total_potential_revenue": 2775.0,
    "generated_at": "2025-08-04T07:44:45.704144",
    "status": "success"
}
```

## Revenue Forecasting

### RPM-Based Calculations

Each channel has specific RPM (Revenue Per Mille) ranges:

- **YouTube**: $2.0-$8.0 per 1000 views
- **TikTok**: $0.5-$2.0 per 1000 views
- **Instagram**: $1.0-$4.0 per 1000 views
- **LinkedIn**: $3.0-$10.0 per 1000 views
- **Twitter**: $1.5-$5.0 per 1000 views

### Revenue Calculation Formula

```
Monthly Revenue = (Monthly Views / 1000) × Average RPM
Yearly Revenue = Monthly Revenue × 12
```

### Example Calculation

For YouTube with 150,000 monthly views:
- Average RPM: $5.0
- Monthly Revenue: (150,000 / 1000) × $5.0 = $750.00
- Yearly Revenue: $750.00 × 12 = $9,000.00

## Output Files

### Generated Files

1. **Channel Suggestions Analytics**
   - Location: `data/channel_suggestions_analytics.json`
   - Format: JSON array of channel suggestions analytics
   - Content: Revenue metrics, channel breakdown, engagement rates

### File Examples

**Channel Suggestions Analytics Structure:**
```json
[
    {
        "content_id": "ai_automation_trends_2025",
        "original_title": "AI Automation Trends 2025",
        "total_channels": 5,
        "total_potential_revenue": 2775.0,
        "channel_breakdown": {
            "youtube": {
                "revenue": 750.0,
                "views": 150000,
                "engagement_rate": 0.08
            },
            "tiktok": {
                "revenue": 187.5,
                "views": 150000,
                "engagement_rate": 0.12
            },
            "instagram": {
                "revenue": 375.0,
                "views": 150000,
                "engagement_rate": 0.1
            },
            "linkedin": {
                "revenue": 975.0,
                "views": 150000,
                "engagement_rate": 0.06
            },
            "twitter": {
                "revenue": 487.5,
                "views": 150000,
                "engagement_rate": 0.09
            }
        },
        "generated_at": "2025-08-04T07:44:45.704144"
    }
]
```

## Testing

### Test Scripts

1. **Channel Suggestions Test**
   ```bash
   python scripts/test_channel_suggestions.py
   ```

2. **Content Scheduler Test**
   ```bash
   python scripts/test_content_scheduler.py --generation-only
   ```

3. **Manual Testing**
   ```python
   # Test individual components
   from ai import AIModule
   
   # Test AI module
   ai_module = AIModule()
   result = await ai_module.suggest_alternative_channels({
       "title": "Test Content",
       "description": "Test description",
       "content_type": "video"
   })
   ```

### Expected Test Results

- ✅ Channel suggestions generated for all 5 channels
- ✅ Content adaptations created for each channel
- ✅ Revenue forecasts calculated with realistic RPM values
- ✅ Analytics tracked in JSON file
- ✅ Total potential revenue calculated

## Content Adaptation Examples

### YouTube Adaptation
- **Original**: "AI Automation Trends 2025"
- **Adapted**: "AI Automation Trends 2025 - Complete Guide"
- **Script**: 15-minute detailed video with chapters
- **Focus**: Educational, SEO-optimized, comprehensive

### TikTok Adaptation
- **Original**: "AI Automation Trends 2025"
- **Adapted**: "5 AI Trends That Will BLOW Your Mind in 2025"
- **Script**: 30-second viral hook with trending sounds
- **Focus**: Viral, trending, hook-based

### LinkedIn Adaptation
- **Original**: "AI Automation Trends 2025"
- **Adapted**: "How AI Automation is Transforming Business in 2025"
- **Script**: 2-minute professional video with business insights
- **Focus**: Professional, thought leadership, business value

## Performance Metrics

### Channel Performance Comparison

| Channel | Avg RPM | Engagement Rate | Monthly Revenue | Best Use Case |
|---------|---------|----------------|-----------------|---------------|
| YouTube | $5.00 | 8.0% | $750.00 | Educational content |
| TikTok | $1.25 | 12.0% | $187.50 | Viral short content |
| Instagram | $2.50 | 10.0% | $375.00 | Visual storytelling |
| LinkedIn | $6.50 | 6.0% | $975.00 | Professional content |
| Twitter | $3.25 | 9.0% | $487.50 | Conversational content |

### Revenue Optimization Tips

1. **YouTube**: Focus on SEO, longer content, educational value
2. **TikTok**: Use trending sounds, viral hooks, short format
3. **Instagram**: Emphasize visual appeal, stories, reels
4. **LinkedIn**: Professional tone, business insights, thought leadership
5. **Twitter**: Conversational, trending topics, engagement

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Start Ollama if not running
   ollama serve
   ```

2. **Channel Adaptation Failed**
   ```bash
   # Check Ollama model availability
   ollama list
   
   # Pull required model
   ollama pull llama2
   ```

3. **Revenue Calculation Error**
   ```bash
   # Ensure finance module is available
   python -c "from finance import FinanceManager; print('OK')"
   ```

### Error Messages

- `"Error generating channel adaptation"`: Ollama not running or model not available
- `"Error calculating channel revenue forecast"`: Finance module import or calculation error
- `"Error tracking channel suggestions analytics"`: File permission or JSON serialization error

## Performance Optimization

### Optimization Tips

1. **Ollama Performance**
   ```bash
   # Use smaller models for faster generation
   ollama pull llama2:7b
   
   # Increase context window for better results
   export OLLAMA_CONTEXT_SIZE=4096
   ```

2. **Content Adaptation**
   ```python
   # Cache channel configurations for faster processing
   # Use fallback adaptations when Ollama is unavailable
   ```

3. **Revenue Forecasting**
   ```python
   # Update RPM ranges based on real performance data
   # Adjust engagement rates based on actual metrics
   ```

### Monitoring

1. **Analytics Monitoring**
   ```python
   # Monitor analytics file size
   import os
   size = os.path.getsize("data/channel_suggestions_analytics.json")
   print(f"Analytics file size: {size} bytes")
   ```

2. **Revenue Tracking**
   ```python
   # Track total potential revenue trends
   # Monitor channel performance over time
   ```

## Future Enhancements

### Planned Features

1. **Advanced Content Adaptation**
   - Multi-modal AI for visual content adaptation
   - Voice-over generation for video content
   - Automatic thumbnail generation

2. **Enhanced Revenue Forecasting**
   - Real-time RPM data integration
   - Seasonal adjustment factors
   - Competitor analysis integration

3. **Channel-Specific Templates**
   - Pre-built content templates for each channel
   - Industry-specific adaptation strategies
   - A/B testing for content variations

4. **Performance Analytics**
   - Real-time performance tracking
   - Cross-channel performance comparison
   - ROI optimization recommendations

### API Extensions

```python
# Future API endpoints
@app.post("/api/v1/channel-suggestions/generate")
async def generate_channel_suggestions(content: ContentRequest):
    pass

@app.get("/api/v1/channel-suggestions/analytics")
async def get_channel_analytics(timeframe: str = "30d"):
    pass

@app.post("/api/v1/channel-suggestions/optimize")
async def optimize_channel_strategy(content_id: str):
    pass
```

## Security Considerations

### Data Protection

1. **Local Processing**: All AI processing happens locally with Ollama
2. **No External Dependencies**: No API keys required for core functionality
3. **Data Privacy**: Channel suggestions and analytics stored locally
4. **Secure File Handling**: Proper file permissions and validation

### Best Practices

1. **Environment Variables**: Use environment variables for sensitive configuration
2. **Input Validation**: Validate all user inputs and file operations
3. **Error Handling**: Comprehensive error handling without exposing sensitive data
4. **Logging**: Secure logging without exposing content details

## Conclusion

The Channel Suggestions feature provides a comprehensive, cost-free solution for multi-channel content distribution with intelligent adaptations and revenue forecasting. It integrates seamlessly with the existing content scheduler and provides valuable insights for content strategy optimization.

The system is designed to be:
- **Comprehensive**: Analyzes all 5 major social media channels
- **Intelligent**: Uses AI for channel-specific content adaptation
- **Financial**: Includes revenue forecasting with realistic RPM calculations
- **Scalable**: Integrates with scheduler for continuous operation
- **Analytics-driven**: Tracks performance for continuous improvement

For support or questions, refer to the main project documentation or create an issue in the repository. 