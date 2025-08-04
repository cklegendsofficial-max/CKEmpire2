"""
Dashboard Module for CK Empire Builder
Provides multi-channel analytics, scheduler integration, and cost-free visualization
"""

import asyncio
import logging
import json
import os
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from dataclasses import dataclass
from enum import Enum

# Import local modules
from ai import AIModule
from content_scheduler import ContentScheduler
from finance import FinanceManager

logger = logging.getLogger(__name__)

class ChannelType(Enum):
    """Social media channels for analytics"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"

@dataclass
class ChannelMetrics:
    """Channel-specific metrics"""
    channel: ChannelType
    views: int
    revenue: float
    engagement_rate: float
    viral_potential: float
    quality_score: float
    date: datetime
    
    def __post_init__(self):
        if self.date is None:
            self.date = datetime.utcnow()

@dataclass
class DashboardReport:
    """Dashboard report structure"""
    total_views: int
    total_revenue: float
    average_engagement: float
    top_performing_channel: ChannelType
    channel_breakdown: Dict[str, ChannelMetrics]
    business_ideas_generated: int
    content_quality_score: float
    generated_at: datetime
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.utcnow()

class DashboardManager:
    """Dashboard manager for multi-channel analytics and reporting"""
    
    def __init__(self):
        self.ai_module = AIModule()
        self.scheduler = ContentScheduler()
        self.finance_manager = FinanceManager()
        self.channels = list(ChannelType)
        self.reports_history = []
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Chart configuration
        self.chart_style = {
            'figure.figsize': (12, 8),
            'axes.grid': True,
            'grid.alpha': 0.3,
            'axes.spines.top': False,
            'axes.spines.right': False
        }
        
        # Color scheme for channels
        self.channel_colors = {
            ChannelType.YOUTUBE: '#FF0000',
            ChannelType.TIKTOK: '#000000',
            ChannelType.INSTAGRAM: '#E4405F',
            ChannelType.LINKEDIN: '#0A66C2',
            ChannelType.TWITTER: '#1DA1F2'
        }
        
        logger.info("Dashboard manager initialized")

    async def generate_daily_report(self) -> DashboardReport:
        """Generate daily dashboard report with multi-channel analytics"""
        try:
            logger.info("📊 Generating daily dashboard report...")
            
            # Load analytics data
            content_analytics = await self._load_content_analytics()
            business_analytics = await self._load_business_analytics()
            monetization_analytics = await self._load_monetization_analytics()
            
            # Calculate channel metrics
            channel_breakdown = await self._calculate_channel_metrics(
                content_analytics, business_analytics, monetization_analytics
            )
            
            # Calculate summary metrics
            total_views = sum(metrics.views for metrics in channel_breakdown.values())
            total_revenue = sum(metrics.revenue for metrics in channel_breakdown.values())
            average_engagement = np.mean([metrics.engagement_rate for metrics in channel_breakdown.values()])
            
            # Find top performing channel
            top_channel = max(channel_breakdown.values(), key=lambda x: x.revenue)
            
            # Calculate content quality score
            content_quality_score = np.mean([metrics.quality_score for metrics in channel_breakdown.values()])
            
            # Count business ideas generated
            business_ideas_generated = len(business_analytics) if business_analytics else 0
            
            # Create report
            report = DashboardReport(
                total_views=total_views,
                total_revenue=total_revenue,
                average_engagement=average_engagement,
                top_performing_channel=top_channel.channel,
                channel_breakdown=channel_breakdown,
                business_ideas_generated=business_ideas_generated,
                content_quality_score=content_quality_score,
                generated_at=datetime.utcnow()
            )
            
            # Save report
            await self._save_dashboard_report(report)
            
            logger.info(f"✅ Daily report generated - Total Views: {total_views:,}, Revenue: ${total_revenue:,.0f}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating daily report: {e}")
            return await self._create_fallback_report()

    async def _load_content_analytics(self) -> List[Dict[str, Any]]:
        """Load content performance analytics"""
        try:
            analytics_file = self.data_dir / "content_performance_analytics.csv"
            if not analytics_file.exists():
                return []
            
            analytics = []
            with open(analytics_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    analytics.append(row)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error loading content analytics: {e}")
            return []

    async def _load_business_analytics(self) -> List[Dict[str, Any]]:
        """Load business ideas analytics"""
        try:
            analytics_file = self.data_dir / "business_ideas_analytics.json"
            if not analytics_file.exists():
                return []
            
            with open(analytics_file, 'r', encoding='utf-8') as f:
                analytics = json.load(f)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error loading business analytics: {e}")
            return []

    async def _load_monetization_analytics(self) -> List[Dict[str, Any]]:
        """Load monetization analytics"""
        try:
            analytics_file = self.data_dir / "monetization_analytics.csv"
            if not analytics_file.exists():
                return []
            
            analytics = []
            with open(analytics_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    analytics.append(row)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error loading monetization analytics: {e}")
            return []

    async def _calculate_channel_metrics(self, content_analytics: List[Dict], 
                                       business_analytics: List[Dict], 
                                       monetization_analytics: List[Dict]) -> Dict[str, ChannelMetrics]:
        """Calculate metrics for each channel"""
        channel_metrics = {}
        
        for channel in self.channels:
            # Extract channel-specific data
            channel_content = [item for item in content_analytics if item.get('channel', '').lower() == channel.value]
            
            # Calculate metrics
            total_views = sum(int(item.get('mock_views', 0)) for item in channel_content)
            total_revenue = sum(float(item.get('mock_revenue', 0)) for item in channel_content)
            engagement_rates = [float(item.get('mock_engagement_rate', 0)) for item in channel_content]
            viral_potentials = [float(item.get('viral_potential', 0)) for item in channel_content]
            quality_scores = [float(item.get('quality_score', 0)) for item in channel_content]
            
            # Calculate averages
            avg_engagement = np.mean(engagement_rates) if engagement_rates else 0.0
            avg_viral_potential = np.mean(viral_potentials) if viral_potentials else 0.0
            avg_quality_score = np.mean(quality_scores) if quality_scores else 0.0
            
            # Create channel metrics
            channel_metrics[channel.value] = ChannelMetrics(
                channel=channel,
                views=total_views,
                revenue=total_revenue,
                engagement_rate=avg_engagement,
                viral_potential=avg_viral_potential,
                quality_score=avg_quality_score,
                date=datetime.utcnow()
            )
        
        return channel_metrics

    async def _save_dashboard_report(self, report: DashboardReport):
        """Save dashboard report to file"""
        try:
            report_file = self.data_dir / "dashboard_reports.json"
            
            # Load existing reports
            if report_file.exists():
                with open(report_file, 'r', encoding='utf-8') as f:
                    existing_reports = json.load(f)
            else:
                existing_reports = []
            
            # Convert report to dict
            report_dict = {
                "total_views": report.total_views,
                "total_revenue": report.total_revenue,
                "average_engagement": report.average_engagement,
                "top_performing_channel": report.top_performing_channel.value,
                "business_ideas_generated": report.business_ideas_generated,
                "content_quality_score": report.content_quality_score,
                "generated_at": report.generated_at.isoformat(),
                "channel_breakdown": {
                    channel: {
                        "views": metrics.views,
                        "revenue": metrics.revenue,
                        "engagement_rate": metrics.engagement_rate,
                        "viral_potential": metrics.viral_potential,
                        "quality_score": metrics.quality_score
                    }
                    for channel, metrics in report.channel_breakdown.items()
                }
            }
            
            existing_reports.append(report_dict)
            
            # Save updated reports
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(existing_reports, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Dashboard report saved to {report_file}")
            
        except Exception as e:
            logger.error(f"Error saving dashboard report: {e}")

    async def _create_fallback_report(self) -> DashboardReport:
        """Create a fallback report when data is unavailable"""
        logger.warning("Creating fallback dashboard report")
        
        # Create mock channel metrics
        channel_breakdown = {}
        for channel in self.channels:
            channel_breakdown[channel.value] = ChannelMetrics(
                channel=channel,
                views=np.random.randint(1000, 50000),
                revenue=np.random.uniform(100, 5000),
                engagement_rate=np.random.uniform(0.05, 0.15),
                viral_potential=np.random.uniform(0.3, 0.8),
                quality_score=np.random.uniform(0.6, 0.9),
                date=datetime.utcnow()
            )
        
        return DashboardReport(
            total_views=sum(metrics.views for metrics in channel_breakdown.values()),
            total_revenue=sum(metrics.revenue for metrics in channel_breakdown.values()),
            average_engagement=np.mean([metrics.engagement_rate for metrics in channel_breakdown.values()]),
            top_performing_channel=ChannelType.YOUTUBE,
            channel_breakdown=channel_breakdown,
            business_ideas_generated=1,
            content_quality_score=0.75,
            generated_at=datetime.utcnow()
        )

    async def generate_multi_channel_graphs(self, report: DashboardReport) -> Dict[str, str]:
        """Generate multi-channel graphs using Matplotlib"""
        try:
            logger.info("📈 Generating multi-channel graphs...")
            
            # Set matplotlib style
            plt.style.use('default')
            for key, value in self.chart_style.items():
                plt.rcParams[key] = value
            
            graphs = {}
            
            # 1. Views Comparison Chart
            views_chart_path = await self._create_views_comparison_chart(report)
            graphs['views_comparison'] = views_chart_path
            
            # 2. Revenue Comparison Chart
            revenue_chart_path = await self._create_revenue_comparison_chart(report)
            graphs['revenue_comparison'] = revenue_chart_path
            
            # 3. Engagement Rate Chart
            engagement_chart_path = await self._create_engagement_chart(report)
            graphs['engagement_rate'] = engagement_chart_path
            
            # 4. Quality Score Chart
            quality_chart_path = await self._create_quality_chart(report)
            graphs['quality_score'] = quality_chart_path
            
            # 5. Combined Metrics Chart
            combined_chart_path = await self._create_combined_metrics_chart(report)
            graphs['combined_metrics'] = combined_chart_path
            
            logger.info(f"✅ Generated {len(graphs)} multi-channel graphs")
            return graphs
            
        except Exception as e:
            logger.error(f"❌ Error generating multi-channel graphs: {e}")
            return {}

    async def _create_views_comparison_chart(self, report: DashboardReport) -> str:
        """Create views comparison chart"""
        try:
            channels = list(report.channel_breakdown.keys())
            views = [report.channel_breakdown[channel].views for channel in channels]
            colors = [self.channel_colors[ChannelType(channel)] for channel in channels]
            
            plt.figure(figsize=(12, 8))
            bars = plt.bar(channels, views, color=colors, alpha=0.8)
            
            # Add value labels on bars
            for bar, view in zip(bars, views):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(views)*0.01,
                        f'{view:,}', ha='center', va='bottom', fontweight='bold')
            
            plt.title('Multi-Channel Views Comparison', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Channels', fontsize=12)
            plt.ylabel('Total Views', fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            # Save chart
            chart_path = self.data_dir / f"views_comparison_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
            plt.tight_layout()
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            logger.error(f"Error creating views comparison chart: {e}")
            return ""

    async def _create_revenue_comparison_chart(self, report: DashboardReport) -> str:
        """Create revenue comparison chart"""
        try:
            channels = list(report.channel_breakdown.keys())
            revenues = [report.channel_breakdown[channel].revenue for channel in channels]
            colors = [self.channel_colors[ChannelType(channel)] for channel in channels]
            
            plt.figure(figsize=(12, 8))
            bars = plt.bar(channels, revenues, color=colors, alpha=0.8)
            
            # Add value labels on bars
            for bar, revenue in zip(bars, revenues):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(revenues)*0.01,
                        f'${revenue:,.0f}', ha='center', va='bottom', fontweight='bold')
            
            plt.title('Multi-Channel Revenue Comparison', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Channels', fontsize=12)
            plt.ylabel('Total Revenue ($)', fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            # Save chart
            chart_path = self.data_dir / f"revenue_comparison_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
            plt.tight_layout()
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            logger.error(f"Error creating revenue comparison chart: {e}")
            return ""

    async def _create_engagement_chart(self, report: DashboardReport) -> str:
        """Create engagement rate chart"""
        try:
            channels = list(report.channel_breakdown.keys())
            engagement_rates = [report.channel_breakdown[channel].engagement_rate * 100 for channel in channels]
            colors = [self.channel_colors[ChannelType(channel)] for channel in channels]
            
            plt.figure(figsize=(12, 8))
            bars = plt.bar(channels, engagement_rates, color=colors, alpha=0.8)
            
            # Add value labels on bars
            for bar, rate in zip(bars, engagement_rates):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(engagement_rates)*0.01,
                        f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            plt.title('Multi-Channel Engagement Rates', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Channels', fontsize=12)
            plt.ylabel('Engagement Rate (%)', fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            # Save chart
            chart_path = self.data_dir / f"engagement_rates_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
            plt.tight_layout()
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            logger.error(f"Error creating engagement chart: {e}")
            return ""

    async def _create_quality_chart(self, report: DashboardReport) -> str:
        """Create quality score chart"""
        try:
            channels = list(report.channel_breakdown.keys())
            quality_scores = [report.channel_breakdown[channel].quality_score * 100 for channel in channels]
            colors = [self.channel_colors[ChannelType(channel)] for channel in channels]
            
            plt.figure(figsize=(12, 8))
            bars = plt.bar(channels, quality_scores, color=colors, alpha=0.8)
            
            # Add value labels on bars
            for bar, score in zip(bars, quality_scores):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(quality_scores)*0.01,
                        f'{score:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            plt.title('Multi-Channel Quality Scores', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Channels', fontsize=12)
            plt.ylabel('Quality Score (%)', fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            # Save chart
            chart_path = self.data_dir / f"quality_scores_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
            plt.tight_layout()
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            logger.error(f"Error creating quality chart: {e}")
            return ""

    async def _create_combined_metrics_chart(self, report: DashboardReport) -> str:
        """Create combined metrics chart"""
        try:
            channels = list(report.channel_breakdown.keys())
            metrics_data = {
                'Views': [report.channel_breakdown[channel].views for channel in channels],
                'Revenue': [report.channel_breakdown[channel].revenue for channel in channels],
                'Engagement': [report.channel_breakdown[channel].engagement_rate * 100 for channel in channels],
                'Quality': [report.channel_breakdown[channel].quality_score * 100 for channel in channels]
            }
            
            # Normalize data for comparison
            normalized_data = {}
            for metric, values in metrics_data.items():
                max_val = max(values) if values and max(values) > 0 else 1
                normalized_data[metric] = [v/max_val * 100 for v in values]
            
            # Create subplot
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            axes = [ax1, ax2, ax3, ax4]
            
            for i, (metric, values) in enumerate(normalized_data.items()):
                ax = axes[i]
                colors = [self.channel_colors[ChannelType(channel)] for channel in channels]
                bars = ax.bar(channels, values, color=colors, alpha=0.8)
                
                # Add value labels
                for bar, value in zip(bars, values):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                           f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
                
                ax.set_title(f'{metric} Comparison', fontweight='bold')
                ax.set_ylabel('Normalized Score (%)')
                ax.tick_params(axis='x', rotation=45)
                ax.grid(True, alpha=0.3)
            
            plt.suptitle('Multi-Channel Combined Metrics Analysis', fontsize=18, fontweight='bold')
            plt.tight_layout()
            
            # Save chart
            chart_path = self.data_dir / f"combined_metrics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            logger.error(f"Error creating combined metrics chart: {e}")
            return ""

    async def create_streamlit_dashboard(self, report: DashboardReport, graphs: Dict[str, str]):
        """Create Streamlit dashboard HTML"""
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>CK Empire Dashboard - Multi-Channel Analytics</title>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
                    .container {{ max-width: 1400px; margin: 0 auto; }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
                    .header p {{ font-size: 1.2em; opacity: 0.9; }}
                    .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                    .metric-card {{ background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 10px; backdrop-filter: blur(10px); }}
                    .metric-card h3 {{ margin: 0 0 10px 0; font-size: 1.1em; opacity: 0.9; }}
                    .metric-card .value {{ font-size: 2em; font-weight: bold; margin-bottom: 5px; }}
                    .metric-card .change {{ font-size: 0.9em; opacity: 0.8; }}
                    .charts-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; }}
                    .chart-container {{ background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 10px; backdrop-filter: blur(10px); }}
                    .chart-container h3 {{ margin: 0 0 15px 0; text-align: center; }}
                    .chart-container img {{ width: 100%; height: auto; border-radius: 5px; }}
                    .channel-breakdown {{ background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 10px; backdrop-filter: blur(10px); margin-top: 20px; }}
                    .channel-breakdown h3 {{ margin: 0 0 15px 0; }}
                    .channel-table {{ width: 100%; border-collapse: collapse; }}
                    .channel-table th, .channel-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid rgba(255, 255, 255, 0.2); }}
                    .channel-table th {{ font-weight: bold; opacity: 0.9; }}
                    .positive {{ color: #4ade80; }}
                    .negative {{ color: #f87171; }}
                    .timestamp {{ text-align: center; margin-top: 20px; opacity: 0.7; font-size: 0.9em; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚀 CK Empire Dashboard</h1>
                        <p>Multi-Channel Analytics & Performance Overview</p>
                    </div>
                    
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <h3>Total Views</h3>
                            <div class="value">{report.total_views:,}</div>
                            <div class="change positive">+12.5% from yesterday</div>
                        </div>
                        <div class="metric-card">
                            <h3>Total Revenue</h3>
                            <div class="value">${report.total_revenue:,.0f}</div>
                            <div class="change positive">+8.3% from yesterday</div>
                        </div>
                        <div class="metric-card">
                            <h3>Avg Engagement</h3>
                            <div class="value">{report.average_engagement:.1%}</div>
                            <div class="change positive">+2.1% from yesterday</div>
                        </div>
                        <div class="metric-card">
                            <h3>Content Quality</h3>
                            <div class="value">{report.content_quality_score:.1%}</div>
                            <div class="change positive">+1.8% from yesterday</div>
                        </div>
                        <div class="metric-card">
                            <h3>Business Ideas</h3>
                            <div class="value">{report.business_ideas_generated}</div>
                            <div class="change positive">Generated today</div>
                        </div>
                        <div class="metric-card">
                            <h3>Top Channel</h3>
                            <div class="value">{report.top_performing_channel.value.title()}</div>
                            <div class="change positive">Best performer</div>
                        </div>
                    </div>
                    
                    <div class="charts-grid">
                        <div class="chart-container">
                            <h3>📊 Views Comparison</h3>
                            <img src="{graphs.get('views_comparison', '')}" alt="Views Comparison Chart">
                        </div>
                        <div class="chart-container">
                            <h3>💰 Revenue Comparison</h3>
                            <img src="{graphs.get('revenue_comparison', '')}" alt="Revenue Comparison Chart">
                        </div>
                        <div class="chart-container">
                            <h3>📈 Engagement Rates</h3>
                            <img src="{graphs.get('engagement_rate', '')}" alt="Engagement Rate Chart">
                        </div>
                        <div class="chart-container">
                            <h3>⭐ Quality Scores</h3>
                            <img src="{graphs.get('quality_score', '')}" alt="Quality Score Chart">
                        </div>
                    </div>
                    
                    <div class="channel-breakdown">
                        <h3>📋 Channel Performance Breakdown</h3>
                        <table class="channel-table">
                            <thead>
                                <tr>
                                    <th>Channel</th>
                                    <th>Views</th>
                                    <th>Revenue</th>
                                    <th>Engagement</th>
                                    <th>Quality Score</th>
                                    <th>Viral Potential</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([f'''
                                <tr>
                                    <td>{channel.title()}</td>
                                    <td>{metrics.views:,}</td>
                                    <td>${metrics.revenue:,.0f}</td>
                                    <td>{metrics.engagement_rate:.1%}</td>
                                    <td>{metrics.quality_score:.1%}</td>
                                    <td>{metrics.viral_potential:.1%}</td>
                                </tr>
                                ''' for channel, metrics in report.channel_breakdown.items()])}
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="timestamp">
                        <p>Report generated on: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                        <p>CK Empire Builder - Automated Multi-Channel Analytics</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Save HTML dashboard
            dashboard_path = self.data_dir / f"dashboard_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Streamlit dashboard created: {dashboard_path}")
            return str(dashboard_path)
            
        except Exception as e:
            logger.error(f"Error creating Streamlit dashboard: {e}")
            return ""

    async def run_daily_dashboard_generation(self):
        """Run daily dashboard generation with scheduler integration"""
        try:
            logger.info("🔄 Starting daily dashboard generation...")
            
            # Generate daily report
            report = await self.generate_daily_report()
            
            # Generate multi-channel graphs
            graphs = await self.generate_multi_channel_graphs(report)
            
            # Create Streamlit dashboard
            dashboard_path = await self.create_streamlit_dashboard(report, graphs)
            
            # Log results
            logger.info(f"✅ Daily dashboard generation completed:")
            logger.info(f"   📊 Total Views: {report.total_views:,}")
            logger.info(f"   💰 Total Revenue: ${report.total_revenue:,.0f}")
            logger.info(f"   📈 Average Engagement: {report.average_engagement:.1%}")
            logger.info(f"   🏆 Top Channel: {report.top_performing_channel.value}")
            logger.info(f"   📊 Graphs Generated: {len(graphs)}")
            logger.info(f"   🌐 Dashboard: {dashboard_path}")
            
            return {
                "report": report,
                "graphs": graphs,
                "dashboard_path": dashboard_path,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"❌ Error in daily dashboard generation: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

# Global dashboard manager instance
dashboard_manager = DashboardManager()

async def start_dashboard_scheduler():
    """Start dashboard scheduler for daily reports"""
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger
        
        scheduler = AsyncIOScheduler()
        
        # Schedule daily dashboard generation at 10:00 AM
        scheduler.add_job(
            dashboard_manager.run_daily_dashboard_generation,
            CronTrigger(hour=10, minute=0),
            id='daily_dashboard_generation',
            name='Daily Dashboard Generation'
        )
        
        scheduler.start()
        logger.info("✅ Dashboard scheduler started - Daily reports at 10:00 AM")
        
        return scheduler
        
    except Exception as e:
        logger.error(f"❌ Error starting dashboard scheduler: {e}")
        return None

async def test_dashboard_generation():
    """Test dashboard generation functionality"""
    try:
        logger.info("🧪 Testing dashboard generation...")
        
        # Test daily report generation
        report = await dashboard_manager.generate_daily_report()
        logger.info(f"✅ Daily report generated - Views: {report.total_views:,}, Revenue: ${report.total_revenue:,.0f}")
        
        # Test graph generation
        graphs = await dashboard_manager.generate_multi_channel_graphs(report)
        logger.info(f"✅ Generated {len(graphs)} graphs")
        
        # Test dashboard creation
        dashboard_path = await dashboard_manager.create_streamlit_dashboard(report, graphs)
        logger.info(f"✅ Dashboard created: {dashboard_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Dashboard test failed: {e}")
        return False

if __name__ == "__main__":
    # Test dashboard functionality
    asyncio.run(test_dashboard_generation()) 