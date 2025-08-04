"""
Content Scheduler Module for CK Empire Builder
Uses APScheduler to generate viral content ideas for multiple channels daily
"""

import asyncio
import logging
import json
import os
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Import AI module
from ai import AIModule, ContentIdea, ContentType

logger = logging.getLogger(__name__)

class ChannelType(Enum):
    """Social media channels for content distribution"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"

@dataclass
class RepurposedContent:
    """Repurposed content for different channels"""
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
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class ContentPerformance:
    """Content performance tracking data"""
    content_id: str
    title: str
    channel: str
    viral_potential: float
    quality_score: float
    mock_views: int
    mock_engagement_rate: float
    mock_revenue: float
    created_at: datetime
    performance_date: datetime = None
    
    def __post_init__(self):
        if self.performance_date is None:
            self.performance_date = datetime.utcnow()

class ContentScheduler:
    """Content scheduler using APScheduler for automated content generation"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.ai_module = AIModule()
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.channels = list(ChannelType)
        self.content_history = []
        self.performance_data = []
        self.is_running = False
        self.quality_threshold = 0.7  # Viral potential threshold
        
        # Platform-specific configurations
        self.platform_configs = {
            ChannelType.YOUTUBE: {
                "optimal_length": "10-15 minutes",
                "format": "video",
                "best_time": "15:00-17:00",
                "hashtag_limit": 15,
                "engagement_type": "views, likes, comments",
                "mock_view_range": (1000, 50000),
                "mock_engagement_range": (0.05, 0.15)
            },
            ChannelType.TIKTOK: {
                "optimal_length": "15-60 seconds",
                "format": "short_video",
                "best_time": "19:00-21:00",
                "hashtag_limit": 5,
                "engagement_type": "views, likes, shares",
                "mock_view_range": (5000, 100000),
                "mock_engagement_range": (0.08, 0.25)
            },
            ChannelType.INSTAGRAM: {
                "optimal_length": "30-60 seconds",
                "format": "reel",
                "best_time": "12:00-14:00",
                "hashtag_limit": 30,
                "engagement_type": "likes, comments, saves",
                "mock_view_range": (2000, 30000),
                "mock_engagement_range": (0.06, 0.18)
            },
            ChannelType.LINKEDIN: {
                "optimal_length": "1-3 minutes",
                "format": "professional_video",
                "best_time": "09:00-11:00",
                "hashtag_limit": 5,
                "engagement_type": "likes, comments, shares",
                "mock_view_range": (500, 10000),
                "mock_engagement_range": (0.04, 0.12)
            },
            ChannelType.TWITTER: {
                "optimal_length": "2-3 minutes",
                "format": "thread",
                "best_time": "08:00-10:00",
                "hashtag_limit": 3,
                "engagement_type": "retweets, likes, replies",
                "mock_view_range": (1000, 25000),
                "mock_engagement_range": (0.05, 0.15)
            }
        }
    
    async def start_scheduler(self):
        """Start the content scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # Schedule daily content generation at 6 AM
            self.scheduler.add_job(
                self.generate_daily_content,
                CronTrigger(hour=6, minute=0),
                id="daily_content_generation",
                name="Generate daily viral content for all channels",
                replace_existing=True
            )
            
            # Schedule weekly content planning on Sundays at 5 AM
            self.scheduler.add_job(
                self.plan_weekly_content,
                CronTrigger(day_of_week="sun", hour=5, minute=0),
                id="weekly_content_planning",
                name="Plan weekly content strategy",
                replace_existing=True
            )
            
            # Schedule content performance analysis on Saturdays at 7 AM
            self.scheduler.add_job(
                self.analyze_content_performance,
                CronTrigger(day_of_week="sat", hour=7, minute=0),
                id="content_performance_analysis",
                name="Analyze content performance and optimize",
                replace_existing=True
            )
            
            # Schedule daily performance tracking at 8 PM
            self.scheduler.add_job(
                self.track_daily_performance,
                CronTrigger(hour=20, minute=0),
                id="daily_performance_tracking",
                name="Track daily content performance",
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("✅ Content scheduler started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start content scheduler: {e}")
            raise
    
    async def stop_scheduler(self):
        """Stop the content scheduler"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        try:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("✅ Content scheduler stopped successfully")
        except Exception as e:
            logger.error(f"❌ Failed to stop content scheduler: {e}")
            raise
    
    async def generate_daily_content(self):
        """Generate daily viral content for all channels with quality checks"""
        logger.info("🚀 Starting daily content generation with quality checks...")
        
        try:
            # Generate one viral content idea
            viral_idea = await self._generate_viral_idea()
            if not viral_idea:
                logger.error("❌ Failed to generate viral idea")
                return
            
            # Quality check for viral potential
            quality_result = await self._assess_content_quality(viral_idea)
            if not quality_result.get("passed", False):
                logger.warning(f"⚠️ Content quality check failed: {quality_result.get('reason', 'Unknown')}")
                logger.info("🔄 Regenerating content with higher quality focus...")
                viral_idea = await self._generate_viral_idea(quality_focus=True)
                if not viral_idea:
                    logger.error("❌ Failed to regenerate high-quality content")
                    return
            
            # Repurpose for all channels with quality checks
            repurposed_content = []
            for channel in self.channels:
                adapted_content = await self._repurpose_for_channel(viral_idea, channel)
                if adapted_content:
                    # Quality check for repurposed content
                    repurpose_quality = await self._assess_repurposed_quality(adapted_content)
                    if repurpose_quality.get("passed", False):
                        # Add performance tracking data
                        adapted_content = await self._add_performance_tracking(adapted_content)
                        repurposed_content.append(adapted_content)
                        logger.info(f"✅ {channel.value}: Quality passed (Score: {adapted_content.quality_score:.2f})")
                    else:
                        logger.warning(f"⚠️ {channel.value}: Quality check failed - {repurpose_quality.get('reason', 'Unknown')}")
            
            # Generate business idea
            business_idea_result = await self._generate_daily_business_idea()
            
            # Save to content history
            self.content_history.extend(repurposed_content)
            
            # Track performance analytics
            await self._track_content_analytics(repurposed_content)
            
            # Log results
            logger.info(f"✅ Generated {len(repurposed_content)} quality-approved content pieces")
            for content in repurposed_content:
                logger.info(f"📱 {content.channel.value}: {content.adapted_title} (Quality: {content.quality_score:.2f})")
            
            # Save to file for persistence
            await self._save_content_to_file(repurposed_content)
            
            # Generate channel suggestions for the viral idea
            channel_suggestions_result = await self._generate_channel_suggestions(viral_idea)
            
            # Log business idea results
            if business_idea_result:
                business_idea = business_idea_result.get("business_idea", {})
                roi_analysis = business_idea_result.get("roi_analysis", {})
                logger.info(f"💼 Business idea: {business_idea.get('title', 'Unknown')}")
                logger.info(f"📊 ROI: {roi_analysis.get('roi_calculation', {}).get('roi_percentage', 0):.2f}%")
            
            # Log channel suggestions results
            if channel_suggestions_result:
                total_revenue = channel_suggestions_result.get("total_potential_revenue", 0)
                logger.info(f"📺 Channel suggestions generated - Total potential revenue: ${total_revenue:.2f}")
                for channel, suggestion in channel_suggestions_result.get("channel_suggestions", {}).items():
                    revenue = suggestion.get("revenue_forecast", {}).get("monthly_revenue", 0)
                    logger.info(f"   📱 {channel.upper()}: ${revenue:.2f}/month")
            
            # Generate monetization forecast for all channels
            monetization_result = await self._generate_daily_monetization_forecast()
            
            # Log monetization results
            if monetization_result:
                total_potential_revenue = monetization_result.get("total_potential_revenue", 0)
                monthly_revenue = monetization_result.get("financial_analysis", {}).get("total_revenue", 0)
                roi_percentage = monetization_result.get("roi_analysis", {}).get("roi_percentage", 0)
                logger.info(f"💰 Monetization forecast generated - Total potential: ${total_potential_revenue:.2f}")
                logger.info(f"📊 Monthly revenue: ${monthly_revenue:.2f}, ROI: {roi_percentage:.2f}%")
                
                # Log channel breakdown
                channel_breakdown = monetization_result.get("financial_analysis", {}).get("channel_breakdown", {})
                for channel, data in channel_breakdown.items():
                    channel_revenue = data.get("total_revenue", 0)
                    logger.info(f"   💰 {channel}: ${channel_revenue:.2f}/month")
            
            # Generate niche content ideas
            niche_content_result = await self._generate_daily_niche_content()
            
            # Log niche content results
            if niche_content_result:
                niche = niche_content_result.get("niche", "Unknown")
                total_ideas = niche_content_result.get("total_ideas", 0)
                average_viral_potential = niche_content_result.get("average_viral_potential", 0.0)
                total_revenue = niche_content_result.get("total_estimated_revenue", 0.0)
                logger.info(f"🎯 Niche content generated for '{niche}' - {total_ideas} ideas")
                logger.info(f"📊 Average viral potential: {average_viral_potential:.2f}")
                logger.info(f"💰 Total estimated revenue: ${total_revenue:.2f}")
            
            # Generate daily dashboard report
            dashboard_result = await self._generate_daily_dashboard_report()
            
            # Log dashboard results
            if dashboard_result:
                report = dashboard_result.get("report", {})
                graphs = dashboard_result.get("graphs", {})
                dashboard_path = dashboard_result.get("dashboard_path", "")
                logger.info(f"📊 Daily dashboard generated - {len(graphs)} graphs created")
                logger.info(f"🌐 Dashboard available at: {dashboard_path}")
                if report:
                    total_views = report.get("total_views", 0)
                    total_revenue = report.get("total_revenue", 0)
                    top_channel = report.get("top_performing_channel", "Unknown")
                    logger.info(f"📈 Total Views: {total_views:,}, Revenue: ${total_revenue:,.0f}")
                    logger.info(f"🏆 Top Channel: {top_channel}")
                
                # Log variation breakdown
                variation_types = niche_content_result.get("variation_types", {})
                for variation_type, count in variation_types.items():
                    logger.info(f"   📝 {variation_type.title()}: {count} ideas")
            
        except Exception as e:
            logger.error(f"❌ Error in daily content generation: {e}")

    async def _assess_content_quality(self, content_idea: ContentIdea) -> Dict[str, Any]:
        """Assess content quality using AI module"""
        try:
            logger.info("🔍 Assessing content quality...")
            
            # Check viral potential threshold
            if content_idea.viral_potential < self.quality_threshold:
                return {
                    "passed": False,
                    "reason": f"Viral potential ({content_idea.viral_potential:.2f}) below threshold ({self.quality_threshold})",
                    "score": content_idea.viral_potential
                }
            
            # Use Ollama for additional quality assessment
            prompt = f"""
            Assess the quality and viral potential of this content idea:
            
            Title: {content_idea.title}
            Description: {content_idea.description}
            Target Audience: {content_idea.target_audience}
            Viral Potential: {content_idea.viral_potential}
            Keywords: {', '.join(content_idea.keywords)}
            
            Evaluate based on:
            1. Viral potential (0-1 scale)
            2. Engagement likelihood
            3. Shareability
            4. Relevance to 2025 trends
            
            Return as JSON:
            {{
                "quality_score": 0.85,
                "viral_potential": 0.82,
                "engagement_likelihood": 0.78,
                "shareability": 0.80,
                "trend_relevance": 0.85,
                "overall_assessment": "high_quality"
            }}
            """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": "llama2",
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("response", "")
                    
                    try:
                        assessment = json.loads(content)
                        quality_score = assessment.get("quality_score", content_idea.viral_potential)
                        
                        # Determine if content passes quality check
                        passed = quality_score >= self.quality_threshold
                        
                        return {
                            "passed": passed,
                            "reason": "Quality assessment completed" if passed else f"Quality score ({quality_score:.2f}) below threshold",
                            "score": quality_score,
                            "assessment": assessment
                        }
                    except json.JSONDecodeError:
                        # Fallback to viral potential check
                        return {
                            "passed": content_idea.viral_potential >= self.quality_threshold,
                            "reason": "Using viral potential as quality indicator",
                            "score": content_idea.viral_potential
                        }
                else:
                    # Fallback to viral potential check
                    return {
                        "passed": content_idea.viral_potential >= self.quality_threshold,
                        "reason": "Using viral potential as quality indicator",
                        "score": content_idea.viral_potential
                    }
                    
        except Exception as e:
            logger.error(f"❌ Error assessing content quality: {e}")
            # Fallback to viral potential check
            return {
                "passed": content_idea.viral_potential >= self.quality_threshold,
                "reason": "Quality assessment failed, using viral potential",
                "score": content_idea.viral_potential
            }

    async def _assess_repurposed_quality(self, repurposed_content: RepurposedContent) -> Dict[str, Any]:
        """Assess quality of repurposed content"""
        try:
            # Calculate quality score based on multiple factors
            viral_score = repurposed_content.viral_potential
            engagement_score = repurposed_content.estimated_engagement
            adaptation_score = 0.8  # Base adaptation score
            
            # Adjust based on channel-specific factors
            config = self.platform_configs[repurposed_content.channel]
            if len(repurposed_content.hashtags) <= config["hashtag_limit"]:
                adaptation_score += 0.1
            
            if repurposed_content.platform_specific_hooks:
                adaptation_score += 0.1
            
            # Calculate overall quality score
            quality_score = (viral_score * 0.4 + engagement_score * 0.4 + adaptation_score * 0.2)
            repurposed_content.quality_score = quality_score
            
            passed = quality_score >= self.quality_threshold
            
            return {
                "passed": passed,
                "reason": f"Quality score ({quality_score:.2f}) {'meets' if passed else 'below'} threshold ({self.quality_threshold})",
                "score": quality_score
            }
            
        except Exception as e:
            logger.error(f"❌ Error assessing repurposed quality: {e}")
            return {
                "passed": repurposed_content.viral_potential >= self.quality_threshold,
                "reason": "Quality assessment failed, using viral potential",
                "score": repurposed_content.viral_potential
            }

    async def _add_performance_tracking(self, content: RepurposedContent) -> RepurposedContent:
        """Add mock performance tracking data to content"""
        try:
            import random
            config = self.platform_configs[content.channel]
            
            # Generate mock views based on channel and viral potential
            view_range = config["mock_view_range"]
            base_views = random.randint(view_range[0], view_range[1])
            viral_multiplier = 1 + (content.viral_potential - 0.5) * 2  # 0.5-1.5x multiplier
            mock_views = int(base_views * viral_multiplier)
            
            # Generate mock engagement rate
            engagement_range = config["mock_engagement_range"]
            base_engagement = random.uniform(engagement_range[0], engagement_range[1])
            quality_multiplier = 1 + (content.quality_score - 0.5) * 0.5  # 0.75-1.25x multiplier
            mock_engagement_rate = min(base_engagement * quality_multiplier, 1.0)
            
            # Update content with performance data
            content.mock_views = mock_views
            content.mock_engagement_rate = mock_engagement_rate
            
            return content
            
        except Exception as e:
            logger.error(f"❌ Error adding performance tracking: {e}")
            # Set default values
            content.mock_views = 1000
            content.mock_engagement_rate = 0.05
            return content

    async def _track_content_analytics(self, content_list: List[RepurposedContent]):
        """Track content analytics and save to CSV"""
        try:
            timestamp = datetime.now()
            
            for content in content_list:
                # Calculate mock revenue (basic calculation)
                mock_revenue = content.mock_views * content.mock_engagement_rate * 0.01  # $0.01 per engagement
                
                performance_data = ContentPerformance(
                    content_id=f"{content.channel.value}_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                    title=content.adapted_title,
                    channel=content.channel.value,
                    viral_potential=content.viral_potential,
                    quality_score=content.quality_score,
                    mock_views=content.mock_views,
                    mock_engagement_rate=content.mock_engagement_rate,
                    mock_revenue=mock_revenue,
                    created_at=content.created_at,
                    performance_date=timestamp
                )
                
                self.performance_data.append(performance_data)
            
            # Save to CSV
            await self._save_performance_to_csv()
            
            logger.info(f"✅ Tracked analytics for {len(content_list)} content pieces")
            
        except Exception as e:
            logger.error(f"❌ Error tracking content analytics: {e}")

    async def _save_performance_to_csv(self):
        """Save performance data to CSV file"""
        try:
            data_dir = "data"
            os.makedirs(data_dir, exist_ok=True)
            
            csv_file = os.path.join(data_dir, "content_performance_analytics.csv")
            
            # Check if file exists to determine if we need headers
            file_exists = os.path.exists(csv_file)
            
            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write headers if file doesn't exist
                if not file_exists:
                    writer.writerow([
                        'content_id', 'title', 'channel', 'viral_potential', 'quality_score',
                        'mock_views', 'mock_engagement_rate', 'mock_revenue', 'created_at', 'performance_date'
                    ])
                
                # Write performance data
                for performance in self.performance_data[-len(self.channels):]:  # Only latest batch
                    writer.writerow([
                        performance.content_id,
                        performance.title,
                        performance.channel,
                        performance.viral_potential,
                        performance.quality_score,
                        performance.mock_views,
                        performance.mock_engagement_rate,
                        performance.mock_revenue,
                        performance.created_at.isoformat(),
                        performance.performance_date.isoformat()
                    ])
            
            logger.info(f"✅ Performance data saved to {csv_file}")
            
        except Exception as e:
            logger.error(f"❌ Error saving performance to CSV: {e}")

    async def track_daily_performance(self):
        """Track daily content performance with mock data"""
        logger.info("📊 Tracking daily content performance...")
        
        try:
            if not self.content_history:
                logger.info("⚠️ No content in history to track")
                return
            
            # Get today's content
            today = datetime.now().date()
            today_content = [
                content for content in self.content_history
                if content.created_at.date() == today
            ]
            
            if not today_content:
                logger.info("⚠️ No content generated today")
                return
            
            # Update mock performance data
            for content in today_content:
                # Simulate performance over time
                import random
                time_factor = random.uniform(0.8, 1.2)  # Simulate time-based variation
                content.mock_views = int(content.mock_views * time_factor)
                content.mock_engagement_rate = min(content.mock_engagement_rate * time_factor, 1.0)
            
            # Track updated analytics
            await self._track_content_analytics(today_content)
            
            # Generate performance summary
            total_views = sum(content.mock_views for content in today_content)
            avg_engagement = sum(content.mock_engagement_rate for content in today_content) / len(today_content)
            total_revenue = sum(content.mock_views * content.mock_engagement_rate * 0.01 for content in today_content)
            
            logger.info(f"📈 Daily Performance Summary:")
            logger.info(f"   Total Views: {total_views:,}")
            logger.info(f"   Avg Engagement: {avg_engagement:.2%}")
            logger.info(f"   Estimated Revenue: ${total_revenue:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Error tracking daily performance: {e}")

    async def _generate_daily_business_idea(self) -> Optional[Dict[str, Any]]:
        """Generate a daily business idea using the AI module"""
        try:
            logger.info("💼 Starting daily business idea generation...")
            
            # Get existing business ideas from analytics file
            existing_ideas = await self._load_existing_business_ideas()
            
            # Generate new business idea
            result = await self.ai_module.generate_and_implement_business_idea(existing_ideas)
            
            if result.get("status") == "success":
                business_idea = result.get("business_idea", {})
                roi_analysis = result.get("roi_analysis", {})
                pdf_path = result.get("pdf_plan_path", "")
                
                logger.info(f"✅ Generated business idea: {business_idea.get('title', 'Unknown')}")
                logger.info(f"📊 ROI: {roi_analysis.get('roi_calculation', {}).get('roi_percentage', 0):.2f}%")
                if pdf_path:
                    logger.info(f"📄 PDF plan: {pdf_path}")
                
                return result
            else:
                logger.error(f"❌ Failed to generate business idea: {result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generating daily business idea: {e}")
            return None

    async def _load_existing_business_ideas(self) -> List[Dict[str, Any]]:
        """Load existing business ideas from analytics file"""
        try:
            from pathlib import Path
            data_dir = Path("data")
            analytics_file = data_dir / "business_ideas_analytics.json"
            
            if analytics_file.exists():
                with open(analytics_file, 'r', encoding='utf-8') as f:
                    existing_analytics = json.load(f)
                    # Convert analytics data to business idea format
                    ideas = []
                    for analytics in existing_analytics[-10:]:  # Last 10 ideas
                        ideas.append({
                            "title": analytics.get("idea_title", "Unknown"),
                            "initial_investment": analytics.get("initial_investment", 0),
                            "projected_revenue_year_3": analytics.get("projected_revenue_year_3", 0),
                            "roi_percentage": analytics.get("roi_percentage", 0)
                        })
                    return ideas
            else:
                return []
                
        except Exception as e:
            logger.error(f"❌ Error loading existing business ideas: {e}")
            return []

    async def _generate_channel_suggestions(self, viral_idea: ContentIdea) -> Optional[Dict[str, Any]]:
        """Generate channel suggestions for viral content idea"""
        try:
            logger.info("📺 Starting channel suggestions generation...")
            
            # Convert ContentIdea to dictionary format
            original_content = {
                "title": viral_idea.title,
                "description": viral_idea.description,
                "content_type": viral_idea.content_type.value,
                "target_audience": viral_idea.target_audience,
                "viral_potential": viral_idea.viral_potential,
                "estimated_revenue": viral_idea.estimated_revenue,
                "keywords": viral_idea.keywords,
                "hashtags": viral_idea.hashtags
            }
            
            # Generate channel suggestions using AI module
            result = await self.ai_module.suggest_alternative_channels(original_content)
            
            if result.get("status") == "success":
                total_revenue = result.get("total_potential_revenue", 0)
                channel_count = len(result.get("channel_suggestions", {}))
                
                logger.info(f"✅ Generated channel suggestions for {channel_count} channels")
                logger.info(f"💰 Total potential revenue: ${total_revenue:.2f}/month")
                
                return result
            else:
                logger.error(f"❌ Failed to generate channel suggestions: {result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generating channel suggestions: {e}")
            return None

    async def _generate_daily_monetization_forecast(self) -> Optional[Dict[str, Any]]:
        """Generate daily monetization forecast for all channels"""
        try:
            logger.info("💰 Starting daily monetization forecast generation...")
            
            # Define the 5 main channels
            channels = ["YouTube", "TikTok", "Instagram", "LinkedIn", "Twitter"]
            
            # Generate monetization strategies using AI module
            result = await self.ai_module.generate_monetization_for_channels(channels)
            
            if result.get("status") == "success":
                total_revenue = result.get("total_potential_revenue", 0)
                channel_count = len(result.get("channels", []))
                
                logger.info(f"✅ Generated monetization forecast for {channel_count} channels")
                logger.info(f"💰 Total potential revenue: ${total_revenue:.2f}/month")
                
                return result
            else:
                logger.error(f"❌ Failed to generate monetization forecast: {result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generating daily monetization forecast: {e}")
            return None

    async def _generate_daily_niche_content(self) -> Optional[Dict[str, Any]]:
        """Generate daily niche content ideas with educational, viral, and lifestyle variations"""
        try:
            logger.info("🎯 Starting daily niche content generation...")
            
            # Popular niches for 2025
            popular_niches = [
                "AI and automation",
                "Sustainable living",
                "Digital nomad lifestyle",
                "Mental health and wellness",
                "Cryptocurrency and blockchain",
                "Remote work productivity",
                "Personal finance",
                "Fitness and nutrition",
                "Travel and adventure",
                "Technology reviews",
                "Business and entrepreneurship",
                "Creative arts and design",
                "Education and learning",
                "Environmental sustainability",
                "Social media marketing"
            ]
            
            # Select a random niche for today
            import random
            selected_niche = random.choice(popular_niches)
            
            # Generate niche content ideas using AI module
            content_ideas = await self.ai_module.generate_niche_content_ideas(selected_niche, channels=5)
            
            if content_ideas:
                # Calculate analytics
                total_viral_potential = sum(idea.viral_potential for idea in content_ideas)
                total_revenue = sum(idea.estimated_revenue for idea in content_ideas)
                average_viral_potential = total_viral_potential / len(content_ideas)
                
                # Count variation types
                variation_types = {}
                for idea in content_ideas:
                    variation_type = "educational"  # default
                    if "viral" in idea.title.lower() or "shock" in idea.title.lower():
                        variation_type = "viral"
                    elif "lifestyle" in idea.title.lower() or "journey" in idea.title.lower():
                        variation_type = "lifestyle"
                    variation_types[variation_type] = variation_types.get(variation_type, 0) + 1
                
                result = {
                    "status": "success",
                    "niche": selected_niche,
                    "total_ideas": len(content_ideas),
                    "average_viral_potential": average_viral_potential,
                    "total_estimated_revenue": total_revenue,
                    "variation_types": variation_types,
                    "content_ideas": [asdict(idea) for idea in content_ideas],
                    "generated_at": datetime.utcnow().isoformat()
                }
                
                logger.info(f"✅ Generated {len(content_ideas)} niche content ideas for '{selected_niche}'")
                logger.info(f"📊 Average viral potential: {average_viral_potential:.2f}")
                logger.info(f"💰 Total estimated revenue: ${total_revenue:.2f}")
                
                return result
            else:
                logger.error(f"❌ Failed to generate niche content for '{selected_niche}'")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generating daily niche content: {e}")
            return None

    async def _generate_daily_dashboard_report(self) -> Optional[Dict[str, Any]]:
        """Generate daily dashboard report with multi-channel analytics"""
        try:
            logger.info("📊 Generating daily dashboard report...")
            
            # Import dashboard manager
            from dashboard import dashboard_manager
            
            # Generate dashboard report
            dashboard_result = await dashboard_manager.run_daily_dashboard_generation()
            
            if dashboard_result and dashboard_result.get("status") == "success":
                logger.info("✅ Daily dashboard report generated successfully")
                return dashboard_result
            else:
                logger.warning("⚠️ Dashboard generation failed or returned no data")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generating dashboard report: {e}")
            return None
    
    async def _generate_viral_idea(self, quality_focus: bool = False) -> Optional[ContentIdea]:
        """Generate one viral content idea using Ollama with optional quality focus"""
        try:
            # Get trending topics for 2025
            trending_topics = [
                "AI automation trends",
                "Sustainable business models",
                "Digital transformation",
                "Remote work optimization",
                "E-commerce evolution",
                "Cryptocurrency adoption",
                "Mental health in tech",
                "Climate tech solutions",
                "Web3 and metaverse",
                "Personal branding strategies"
            ]
            
            # Select a random topic
            import random
            topic = random.choice(trending_topics)
            
            if quality_focus:
                # Enhanced prompt for high-quality content
                prompt = f"""
                Generate a HIGH-QUALITY viral content idea about "{topic}" for 2025.
                
                Focus on:
                - Maximum viral potential (aim for 0.8+ viral score)
                - High engagement likelihood
                - Strong shareability factor
                - Trending relevance for 2025
                - Multi-platform adaptability
                - Revenue generation potential
                
                Return as JSON:
                {{
                    "title": "Highly engaging title",
                    "description": "Compelling description with viral hooks",
                    "content_type": "video",
                    "target_audience": "Specific target audience",
                    "viral_potential": 0.85,
                    "estimated_revenue": 800.0,
                    "keywords": ["trending", "viral", "2025"],
                    "hashtags": ["#trending", "#viral", "#2025"]
                }}
                """
            else:
                # Standard prompt
                prompt = f"""
                Generate a viral content idea about "{topic}" for 2025.
                
                Focus on:
                - Trending topics and viral potential
                - Multi-platform adaptability
                - Engagement optimization
                - Revenue generation potential
                
                Return as JSON:
                {{
                    "title": "Catchy title",
                    "description": "Compelling description",
                    "content_type": "video",
                    "target_audience": "Target audience",
                    "viral_potential": 0.75,
                    "estimated_revenue": 500.0,
                    "keywords": ["keyword1", "keyword2"],
                    "hashtags": ["#trending", "#viral"]
                }}
                """
            
            # Try AI module first
            ideas = await self.ai_module.generate_viral_content_ideas(
                topic=topic,
                count=1,
                content_type=ContentType.VIDEO
            )
            
            if ideas:
                return ideas[0]
            else:
                # Fallback to Ollama if AI module fails
                return await self._generate_with_ollama(topic, quality_focus)
                
        except Exception as e:
            logger.error(f"❌ Failed to generate viral idea: {e}")
            return None
    
    async def _generate_with_ollama(self, topic: str, quality_focus: bool = False) -> Optional[ContentIdea]:
        """Generate content idea using Ollama locally with optional quality focus"""
        try:
            if quality_focus:
                prompt = f"""
                Generate a HIGH-QUALITY viral content idea about "{topic}" for 2025.
                
                Focus on:
                - Maximum viral potential (aim for 0.8+ viral score)
                - High engagement likelihood
                - Strong shareability factor
                - Trending relevance for 2025
                - Multi-platform adaptability
                - Revenue generation potential
                
                Return as JSON:
                {{
                    "title": "Highly engaging title",
                    "description": "Compelling description with viral hooks",
                    "content_type": "video",
                    "target_audience": "Specific target audience",
                    "viral_potential": 0.85,
                    "estimated_revenue": 800.0,
                    "keywords": ["trending", "viral", "2025"],
                    "hashtags": ["#trending", "#viral", "#2025"]
                }}
                """
            else:
                prompt = f"""
                Generate a viral content idea about "{topic}" for 2025.
                
                Focus on:
                - Trending topics and viral potential
                - Multi-platform adaptability
                - Engagement optimization
                - Revenue generation potential
                
                Return as JSON:
                {{
                    "title": "Catchy title",
                    "description": "Compelling description",
                    "content_type": "video",
                    "target_audience": "Target audience",
                    "viral_potential": 0.75,
                    "estimated_revenue": 500.0,
                    "keywords": ["keyword1", "keyword2"],
                    "hashtags": ["#trending", "#viral"]
                }}
                """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": "llama2",
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("response", "")
                    
                    # Parse JSON response
                    try:
                        idea_data = json.loads(content)
                        return ContentIdea(
                            title=idea_data.get("title", "Viral Content Idea"),
                            description=idea_data.get("description", "Engaging content description"),
                            content_type=ContentType(idea_data.get("content_type", "video")),
                            target_audience=idea_data.get("target_audience", "General audience"),
                            viral_potential=idea_data.get("viral_potential", 0.8),
                            estimated_revenue=idea_data.get("estimated_revenue", 300.0),
                            keywords=idea_data.get("keywords", []),
                            hashtags=idea_data.get("hashtags", [])
                        )
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse Ollama response as JSON")
                        return self._create_fallback_idea(topic)
                else:
                    logger.error(f"Ollama API error: {response.status_code}")
                    return self._create_fallback_idea(topic)
                    
        except Exception as e:
            logger.error(f"❌ Ollama generation failed: {e}")
            return self._create_fallback_idea(topic)
    
    def _create_fallback_idea(self, topic: str) -> ContentIdea:
        """Create a fallback content idea"""
        return ContentIdea(
            title=f"Viral {topic.title()} Strategy",
            description=f"Engaging content about {topic} with high viral potential",
            content_type=ContentType.VIDEO,
            target_audience="Tech-savvy professionals",
            viral_potential=0.75,
            estimated_revenue=250.0,
            keywords=[topic, "viral", "trending", "2025"],
            hashtags=[f"#{topic.replace(' ', '')}", "#viral", "#trending"]
        )
    
    async def _repurpose_for_channel(self, original_idea: ContentIdea, channel: ChannelType) -> Optional[RepurposedContent]:
        """Repurpose content for specific channel"""
        try:
            config = self.platform_configs[channel]
            
            # Create channel-specific prompt
            prompt = f"""
            Repurpose this viral content idea for {channel.value}:
            
            Original: {original_idea.title}
            Description: {original_idea.description}
            
            Adapt for {channel.value} with:
            - Optimal length: {config['optimal_length']}
            - Format: {config['format']}
            - Best posting time: {config['best_time']}
            - Hashtag limit: {config['hashtag_limit']}
            - Engagement focus: {config['engagement_type']}
            
            Return as JSON:
            {{
                "adapted_title": "Channel-specific title",
                "adapted_description": "Channel-optimized description",
                "platform_hooks": ["hook1", "hook2"],
                "optimal_posting_time": "HH:MM",
                "hashtags": ["#hashtag1", "#hashtag2"],
                "content_format": "format",
                "estimated_engagement": 0.85
            }}
            """
            
            # Use Ollama for repurposing
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": "llama2",
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("response", "")
                    
                    try:
                        repurpose_data = json.loads(content)
                        return RepurposedContent(
                            original_idea=original_idea,
                            channel=channel,
                            adapted_title=repurpose_data.get("adapted_title", original_idea.title),
                            adapted_description=repurpose_data.get("adapted_description", original_idea.description),
                            platform_specific_hooks=repurpose_data.get("platform_hooks", []),
                            optimal_posting_time=repurpose_data.get("optimal_posting_time", config["best_time"]),
                            hashtags=repurpose_data.get("hashtags", original_idea.hashtags[:config["hashtag_limit"]]),
                            content_format=repurpose_data.get("content_format", config["format"]),
                            estimated_engagement=repurpose_data.get("estimated_engagement", 0.8),
                            viral_potential=original_idea.viral_potential,
                            quality_score=0.0,  # Will be calculated later
                            mock_views=0,  # Will be set later
                            mock_engagement_rate=0.0  # Will be set later
                        )
                    except json.JSONDecodeError:
                        return self._create_fallback_repurpose(original_idea, channel, config)
                else:
                    return self._create_fallback_repurpose(original_idea, channel, config)
                    
        except Exception as e:
            logger.error(f"❌ Failed to repurpose for {channel.value}: {e}")
            return self._create_fallback_repurpose(original_idea, channel, self.platform_configs[channel])
    
    def _create_fallback_repurpose(self, original_idea: ContentIdea, channel: ChannelType, config: Dict[str, Any]) -> RepurposedContent:
        """Create fallback repurposed content"""
        return RepurposedContent(
            original_idea=original_idea,
            channel=channel,
            adapted_title=f"{original_idea.title} - {channel.value.title()} Version",
            adapted_description=f"{original_idea.description} Optimized for {channel.value}",
            platform_specific_hooks=[f"Optimized for {channel.value} audience"],
            optimal_posting_time=config["best_time"],
            hashtags=original_idea.hashtags[:config["hashtag_limit"]],
            content_format=config["format"],
            estimated_engagement=0.75,
            viral_potential=original_idea.viral_potential,
            quality_score=0.0,  # Will be calculated later
            mock_views=0,  # Will be set later
            mock_engagement_rate=0.0  # Will be set later
        )
    
    async def _save_content_to_file(self, content_list: List[RepurposedContent]):
        """Save generated content to file for persistence"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"content_generated_{timestamp}.json"
            
            # Convert to serializable format
            content_data = []
            for content in content_list:
                content_dict = asdict(content)
                content_dict["original_idea"] = asdict(content.original_idea)
                content_dict["channel"] = content.channel.value
                content_dict["created_at"] = content.created_at.isoformat()
                content_data.append(content_dict)
            
            # Save to data directory
            data_dir = "data"
            os.makedirs(data_dir, exist_ok=True)
            
            filepath = os.path.join(data_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(content_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Content saved to {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save content: {e}")
    
    async def plan_weekly_content(self):
        """Plan weekly content strategy"""
        logger.info("📅 Planning weekly content strategy...")
        
        try:
            # Analyze past performance
            performance_data = await self._analyze_weekly_performance()
            
            # Generate weekly strategy
            strategy = await self._generate_weekly_strategy(performance_data)
            
            # Save weekly plan
            await self._save_weekly_plan(strategy)
            
            logger.info("✅ Weekly content strategy planned")
            
        except Exception as e:
            logger.error(f"❌ Error in weekly content planning: {e}")
    
    async def analyze_content_performance(self):
        """Analyze content performance and optimize"""
        logger.info("📊 Analyzing content performance...")
        
        try:
            # Analyze engagement metrics
            metrics = await self._calculate_engagement_metrics()
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(metrics)
            
            # Save analysis report
            await self._save_performance_analysis(metrics, recommendations)
            
            logger.info("✅ Content performance analysis completed")
            
        except Exception as e:
            logger.error(f"❌ Error in content performance analysis: {e}")
    
    async def _analyze_weekly_performance(self) -> Dict[str, Any]:
        """Analyze weekly content performance"""
        # Mock performance data - in real implementation, fetch from analytics
        return {
            "total_content": len(self.content_history),
            "avg_engagement": 0.78,
            "best_performing_channel": "youtube",
            "top_content_types": ["video", "short_video"],
            "engagement_trends": {"youtube": 0.85, "tiktok": 0.72, "instagram": 0.68}
        }
    
    async def _generate_weekly_strategy(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate weekly content strategy based on performance"""
        return {
            "focus_channels": ["youtube", "tiktok"],
            "content_themes": ["AI trends", "Business growth", "Tech innovation"],
            "posting_schedule": {
                "youtube": "15:00-17:00",
                "tiktok": "19:00-21:00",
                "instagram": "12:00-14:00"
            },
            "engagement_goals": {
                "youtube": 0.85,
                "tiktok": 0.75,
                "instagram": 0.70
            }
        }
    
    async def _save_weekly_plan(self, strategy: Dict[str, Any]):
        """Save weekly content plan"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"weekly_plan_{timestamp}.json"
        
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(strategy, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Weekly plan saved to {filepath}")
    
    async def _calculate_engagement_metrics(self) -> Dict[str, Any]:
        """Calculate engagement metrics"""
        return {
            "total_views": 15000,
            "total_engagement": 0.78,
            "channel_performance": {
                "youtube": {"views": 8000, "engagement": 0.85},
                "tiktok": {"views": 4000, "engagement": 0.72},
                "instagram": {"views": 3000, "engagement": 0.68}
            },
            "top_performing_content": [
                {"title": "AI Automation Trends", "engagement": 0.92},
                {"title": "Business Growth Strategies", "engagement": 0.88}
            ]
        }
    
    async def _generate_optimization_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if metrics["total_engagement"] < 0.8:
            recommendations.append("Focus on more engaging hooks and thumbnails")
        
        if metrics["channel_performance"]["tiktok"]["engagement"] < 0.75:
            recommendations.append("Optimize TikTok content for shorter attention spans")
        
        if metrics["channel_performance"]["youtube"]["views"] < 10000:
            recommendations.append("Improve YouTube SEO and thumbnail optimization")
        
        return recommendations
    
    async def _save_performance_analysis(self, metrics: Dict[str, Any], recommendations: List[str]):
        """Save performance analysis report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_analysis_{timestamp}.json"
        
        report = {
            "metrics": metrics,
            "recommendations": recommendations,
            "analysis_date": datetime.now().isoformat()
        }
        
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Performance analysis saved to {filepath}")
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "is_running": self.is_running,
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in self.scheduler.get_jobs()
            ],
            "content_history_count": len(self.content_history),
            "last_generation": self.content_history[-1].created_at.isoformat() if self.content_history else None
        }
    
    async def manual_generate_content(self) -> List[RepurposedContent]:
        """Manually generate content (for testing)"""
        logger.info("🔄 Manual content generation triggered")
        await self.generate_daily_content()
        return self.content_history[-len(self.channels):] if self.content_history else []

# Global scheduler instance
content_scheduler = ContentScheduler()

async def start_content_scheduler():
    """Start the content scheduler"""
    await content_scheduler.start_scheduler()

async def stop_content_scheduler():
    """Stop the content scheduler"""
    await content_scheduler.stop_scheduler()

if __name__ == "__main__":
    # Test the scheduler
    async def test_scheduler():
        await start_content_scheduler()
        await asyncio.sleep(5)
        content = await content_scheduler.manual_generate_content()
        print(f"Generated {len(content)} content pieces")
        await stop_content_scheduler()
    
    asyncio.run(test_scheduler()) 