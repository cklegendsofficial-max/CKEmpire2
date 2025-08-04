# Content Scheduler Guide

## Overview

The Content Scheduler is an automated content generation system that creates viral content ideas for multiple social media channels daily. It uses APScheduler for scheduling and Ollama for local AI content generation.

## Features

### 🚀 Core Features
- **Daily Content Generation**: Automatically generates content every day at 6 AM
- **Multi-Platform Repurposing**: Creates content for 5 channels from one idea
- **Local AI Processing**: Uses Ollama for cost-free local AI generation
- **Platform Optimization**: Adapts content for each platform's specific requirements
- **Performance Analytics**: Tracks engagement and provides optimization recommendations

### 📱 Supported Channels
1. **YouTube** - Long-form videos (10-15 minutes)
2. **TikTok** - Short videos (15-60 seconds)
3. **Instagram** - Reels (30-60 seconds)
4. **LinkedIn** - Professional videos (1-3 minutes)
5. **Twitter** - Threads (2-3 minutes)

## Architecture

### Components
- **ContentScheduler**: Main scheduler class with APScheduler integration
- **RepurposedContent**: Data structure for channel-specific content
- **ChannelType**: Enum for supported social media platforms
- **Platform Configs**: Channel-specific optimization settings

### Scheduling
- **Daily Generation**: 6:00 AM every day
- **Weekly Planning**: Sundays at 5:00 AM
- **Performance Analysis**: Saturdays at 7:00 AM

## Installation

### Prerequisites
1. **Ollama**: Install and run Ollama locally
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull Llama2 model
   ollama pull llama2
   
   # Start Ollama service
   ollama serve
   ```

2. **Dependencies**: Install APScheduler
   ```bash
   pip install APScheduler==3.10.4
   ```

### Configuration
Set environment variables:
```bash
export OLLAMA_URL="http://localhost:11434"
```

## Usage

### API Endpoints

#### Start Scheduler
```bash
POST /api/v1/content-scheduler/start
```

#### Stop Scheduler
```bash
POST /api/v1/content-scheduler/stop
```

#### Get Status
```bash
GET /api/v1/content-scheduler/status
```

#### Manual Content Generation
```bash
POST /api/v1/content-scheduler/generate-content
```

#### Get Content History
```bash
GET /api/v1/content-scheduler/content-history?limit=50
```

#### Get Analytics
```bash
GET /api/v1/content-scheduler/analytics
```

#### Test Ollama Connection
```bash
POST /api/v1/content-scheduler/test-ollama
```

### Python Usage

```python
from content_scheduler import ContentScheduler, start_content_scheduler

# Initialize scheduler
scheduler = ContentScheduler()

# Start scheduler
await start_content_scheduler()

# Manual content generation
content = await scheduler.manual_generate_content()

# Get status
status = scheduler.get_scheduler_status()
```

## Content Generation Process

### 1. Viral Idea Generation
- Selects from trending 2025 topics
- Uses AI module or Ollama fallback
- Focuses on viral potential and engagement

### 2. Multi-Platform Repurposing
For each channel, adapts content with:
- **Platform-specific titles and descriptions**
- **Optimal posting times**
- **Channel-appropriate hashtags**
- **Format optimization**
- **Engagement predictions**

### 3. Content Optimization
- **YouTube**: SEO-optimized titles, 15 hashtags max
- **TikTok**: Short attention span hooks, 5 hashtags max
- **Instagram**: Visual-first descriptions, 30 hashtags max
- **LinkedIn**: Professional tone, 5 hashtags max
- **Twitter**: Thread format, 3 hashtags max

## Trending Topics (2025)

The scheduler focuses on these viral topics:
- AI automation trends
- Sustainable business models
- Digital transformation
- Remote work optimization
- E-commerce evolution
- Cryptocurrency adoption
- Mental health in tech
- Climate tech solutions
- Web3 and metaverse
- Personal branding strategies

## Platform Configurations

### YouTube
```json
{
  "optimal_length": "10-15 minutes",
  "format": "video",
  "best_time": "15:00-17:00",
  "hashtag_limit": 15,
  "engagement_type": "views, likes, comments"
}
```

### TikTok
```json
{
  "optimal_length": "15-60 seconds",
  "format": "short_video",
  "best_time": "19:00-21:00",
  "hashtag_limit": 5,
  "engagement_type": "views, likes, shares"
}
```

### Instagram
```json
{
  "optimal_length": "30-60 seconds",
  "format": "reel",
  "best_time": "12:00-14:00",
  "hashtag_limit": 30,
  "engagement_type": "likes, comments, saves"
}
```

### LinkedIn
```json
{
  "optimal_length": "1-3 minutes",
  "format": "professional_video",
  "best_time": "09:00-11:00",
  "hashtag_limit": 5,
  "engagement_type": "likes, comments, shares"
}
```

### Twitter
```json
{
  "optimal_length": "2-3 minutes",
  "format": "thread",
  "best_time": "08:00-10:00",
  "hashtag_limit": 3,
  "engagement_type": "retweets, likes, replies"
}
```

## Testing

### Run Full Test
```bash
cd scripts
python test_content_scheduler.py
```

### Test Content Generation Only
```bash
cd scripts
python test_content_scheduler.py --generation-only
```

### Expected Output
```
🚀 Testing Content Scheduler...
✅ Scheduler initialized
✅ Ollama connection successful
✅ Generated 5 content pieces

📱 Content 1 - YOUTUBE:
   Title: AI Automation Trends 2025 - Complete Guide
   Description: Discover the latest AI automation trends...
   Format: video
   Posting Time: 15:00-17:00
   Engagement: 0.85
   Hashtags: #AI, #automation, #trends
```

## Data Storage

### Generated Content
Content is saved to `data/content_generated_YYYYMMDD_HHMMSS.json`

### Weekly Plans
Weekly strategies saved to `data/weekly_plan_YYYYMMDD_HHMMSS.json`

### Performance Analysis
Analytics saved to `data/performance_analysis_YYYYMMDD_HHMMSS.json`

## Monitoring

### Scheduler Status
```python
status = scheduler.get_scheduler_status()
# Returns: is_running, jobs, content_history_count, last_generation
```

### Analytics
```python
# Get content analytics
analytics = await scheduler.get_content_analytics()
# Returns: total_content, avg_engagement, channel_distribution, top_performing_content
```

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   - Ensure Ollama is running: `ollama serve`
   - Check if Llama2 model is installed: `ollama pull llama2`
   - Verify URL: `http://localhost:11434`

2. **No Content Generated**
   - Check AI module availability
   - Verify fallback generation works
   - Review error logs

3. **Scheduler Not Starting**
   - Check APScheduler installation
   - Verify cron job configuration
   - Review system permissions

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Optimization

### Content Quality
- Monitor engagement metrics
- A/B test different hooks
- Optimize posting times
- Track viral potential scores

### System Performance
- Monitor Ollama response times
- Optimize prompt engineering
- Cache frequently used content
- Implement rate limiting

## Future Enhancements

### Planned Features
- **Video Generation**: Automatic video creation from scripts
- **Image Generation**: AI-powered thumbnail creation
- **A/B Testing**: Automated content testing
- **Analytics Integration**: Real platform metrics
- **Content Calendar**: Visual scheduling interface
- **Team Collaboration**: Multi-user content management

### Advanced AI Features
- **Sentiment Analysis**: Content tone optimization
- **Trend Prediction**: Future viral topic forecasting
- **Audience Analysis**: Target demographic optimization
- **Competitor Analysis**: Market positioning insights

## Security Considerations

### Data Privacy
- All content generated locally
- No external API calls (except Ollama)
- Content history stored locally
- No personal data collection

### Access Control
- API endpoint authentication
- Rate limiting on endpoints
- Input validation and sanitization
- Error handling without data exposure

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review error logs
3. Test with the provided test scripts
4. Verify Ollama installation and configuration 