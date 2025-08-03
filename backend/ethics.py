"""
Ethics Module for CK Empire Builder
Handles bias detection and correction using AIF360
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import numpy as np
import pandas as pd
from dataclasses import dataclass
from enum import Enum

# AIF360 imports
try:
    from aif360.datasets import StandardDataset
    from aif360.metrics import ClassificationMetric
    from aif360.algorithms.preprocessing import Reweighing
    from aif360.algorithms.postprocessing import EqOddsPostprocessing
    from aif360.sklearn.metrics import statistical_parity_difference, equalized_odds_difference
    AIF360_AVAILABLE = True
except ImportError:
    AIF360_AVAILABLE = False
    logging.warning("AIF360 not available. Install with: pip install aif360")

from database import get_db, Content, EthicsLog
from models import ContentCreate, ContentResponse

logger = logging.getLogger(__name__)

class BiasType(Enum):
    """Types of bias that can be detected"""
    GENDER = "gender"
    RACE = "race"
    AGE = "age"
    RELIGION = "religion"
    POLITICAL = "political"
    ECONOMIC = "economic"
    CULTURAL = "cultural"

class ContentStatus(Enum):
    """Content status after ethics check"""
    APPROVED = "approved"
    FLAGGED = "flagged"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"

@dataclass
class BiasMetrics:
    """Bias metrics for content analysis"""
    statistical_parity_difference: float
    equalized_odds_difference: float
    average_odds_difference: float
    theil_index: float
    bias_score: float
    fairness_score: float

@dataclass
class EthicsReport:
    """Comprehensive ethics analysis report"""
    content_id: int
    bias_detected: bool
    bias_types: List[BiasType]
    bias_metrics: BiasMetrics
    content_status: ContentStatus
    recommendations: List[str]
    confidence_score: float
    analysis_timestamp: datetime
    flagged_keywords: List[str]
    sensitive_topics: List[str]

class EthicsModule:
    """Main ethics module for bias detection and correction"""
    
    def __init__(self):
        self.bias_threshold = 0.1  # Threshold for bias detection
        self.fairness_threshold = 0.8  # Minimum fairness score
        self.sensitive_keywords = {
            BiasType.GENDER: ["gender", "sex", "male", "female", "man", "woman", "boy", "girl"],
            BiasType.RACE: ["race", "ethnicity", "black", "white", "asian", "hispanic", "african"],
            BiasType.RELIGION: ["religion", "christian", "muslim", "jewish", "hindu", "buddhist"],
            BiasType.POLITICAL: ["politics", "democrat", "republican", "liberal", "conservative"],
            BiasType.ECONOMIC: ["rich", "poor", "wealthy", "poverty", "income", "class"],
            BiasType.CULTURAL: ["culture", "tradition", "custom", "heritage", "nationality"]
        }
        
        if not AIF360_AVAILABLE:
            logger.warning("AIF360 not available. Limited bias detection will be used.")
    
    def analyze_content_ethical(self, content_data: str, content_id: Optional[int] = None) -> EthicsReport:
        """
        Analyze content for ethical issues and bias
        
        Args:
            content_data: The content text to analyze
            content_id: Optional content ID for tracking
            
        Returns:
            EthicsReport with comprehensive analysis
        """
        try:
            logger.info(f"Starting ethics analysis for content {content_id}")
            
            # Step 1: Basic text analysis
            flagged_keywords = self._detect_sensitive_keywords(content_data)
            sensitive_topics = self._identify_sensitive_topics(content_data)
            
            # Step 2: Bias detection using AIF360
            bias_metrics = self._detect_content_bias(content_data)
            
            # Step 3: Determine bias types
            bias_types = self._classify_bias_types(content_data, bias_metrics)
            
            # Step 4: Calculate overall bias score
            bias_score = self._calculate_bias_score(bias_metrics, flagged_keywords)
            fairness_score = 1.0 - bias_score
            
            # Step 5: Determine content status
            content_status = self._determine_content_status(bias_score, fairness_score)
            
            # Step 6: Generate recommendations
            recommendations = self._generate_recommendations(bias_metrics, bias_types, content_status)
            
            # Step 7: Calculate confidence score
            confidence_score = self._calculate_confidence_score(bias_metrics, flagged_keywords)
            
            # Create ethics report
            report = EthicsReport(
                content_id=content_id or 0,
                bias_detected=bias_score > self.bias_threshold,
                bias_types=bias_types,
                bias_metrics=bias_metrics,
                content_status=content_status,
                recommendations=recommendations,
                confidence_score=confidence_score,
                analysis_timestamp=datetime.now(),
                flagged_keywords=flagged_keywords,
                sensitive_topics=sensitive_topics
            )
            
            # Log the analysis
            self._log_ethics_analysis(report)
            
            # Apply revert mechanism if needed
            if content_status == ContentStatus.REJECTED:
                self._revert_unethical_content(content_id)
            
            logger.info(f"Ethics analysis completed. Bias detected: {report.bias_detected}")
            return report
            
        except Exception as e:
            logger.error(f"Error in ethics analysis: {e}")
            # Return a safe default report
            return self._create_default_report(content_id, str(e))
    
    def _detect_sensitive_keywords(self, content: str) -> List[str]:
        """Detect sensitive keywords in content"""
        content_lower = content.lower()
        flagged = []
        
        for bias_type, keywords in self.sensitive_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    flagged.append(f"{bias_type.value}:{keyword}")
        
        return flagged
    
    def _identify_sensitive_topics(self, content: str) -> List[str]:
        """Identify sensitive topics in content"""
        topics = []
        content_lower = content.lower()
        
        # Simple topic detection (in production, use NLP libraries)
        if any(word in content_lower for word in ["discrimination", "bias", "prejudice"]):
            topics.append("discrimination")
        if any(word in content_lower for word in ["hate", "violence", "attack"]):
            topics.append("hate_speech")
        if any(word in content_lower for word in ["stereotype", "generalization"]):
            topics.append("stereotyping")
        
        return topics
    
    def _detect_content_bias(self, content: str) -> BiasMetrics:
        """Detect bias in content using AIF360"""
        if not AIF360_AVAILABLE:
            # Fallback to simple bias detection
            return self._simple_bias_detection(content)
        
        try:
            # Convert content to dataset format
            dataset = self._content_to_dataset(content)
            
            # Calculate bias metrics
            metrics = self._calculate_bias_metrics(dataset)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error in AIF360 bias detection: {e}")
            return self._simple_bias_detection(content)
    
    def _content_to_dataset(self, content: str) -> StandardDataset:
        """Convert content text to AIF360 dataset format"""
        # This is a simplified conversion
        # In production, you'd use proper NLP to extract features
        
        # Split content into sentences/paragraphs
        sentences = content.split('.')
        
        # Create synthetic dataset for demonstration
        # In real implementation, you'd extract actual features
        n_samples = min(len(sentences), 100)
        
        # Create synthetic features (replace with real feature extraction)
        features = np.random.rand(n_samples, 10)
        
        # Create synthetic labels (replace with real classification)
        labels = np.random.randint(0, 2, n_samples)
        
        # Create synthetic protected attributes (gender, race, etc.)
        protected_attributes = np.random.randint(0, 2, (n_samples, 2))
        
        # Create feature names
        feature_names = [f'feature_{i}' for i in range(10)]
        protected_attribute_names = ['gender', 'race']
        
        # Create DataFrame
        df = pd.DataFrame(features, columns=feature_names)
        df['label'] = labels
        df['gender'] = protected_attributes[:, 0]
        df['race'] = protected_attributes[:, 1]
        
        # Create StandardDataset
        dataset = StandardDataset(
            df=df,
            label_name='label',
            favorable_classes=[1],
            protected_attribute_names=protected_attribute_names,
            privileged_classes=[[1], [1]]
        )
        
        return dataset
    
    def _calculate_bias_metrics(self, dataset: StandardDataset) -> BiasMetrics:
        """Calculate bias metrics using AIF360"""
        try:
            # Split dataset
            train, test = dataset.split([0.8], shuffle=True)
            
            # Calculate metrics
            metric = ClassificationMetric(
                dataset=test,
                privileged_groups=[{'gender': 1, 'race': 1}],
                unprivileged_groups=[{'gender': 0, 'race': 0}]
            )
            
            # Extract metrics
            spd = metric.statistical_parity_difference()
            eod = metric.equalized_odds_difference()
            aod = metric.average_odds_difference()
            theil = metric.theil_index()
            
            # Calculate bias score (normalized)
            bias_score = (abs(spd) + abs(eod) + abs(aod)) / 3.0
            
            # Calculate fairness score
            fairness_score = max(0, 1.0 - bias_score)
            
            return BiasMetrics(
                statistical_parity_difference=spd,
                equalized_odds_difference=eod,
                average_odds_difference=aod,
                theil_index=theil,
                bias_score=bias_score,
                fairness_score=fairness_score
            )
            
        except Exception as e:
            logger.error(f"Error calculating bias metrics: {e}")
            return self._simple_bias_detection("")
    
    def _simple_bias_detection(self, content: str) -> BiasMetrics:
        """Simple fallback bias detection when AIF360 is not available"""
        # Simple keyword-based bias detection
        content_lower = content.lower()
        
        # Count sensitive terms
        sensitive_count = sum(1 for keywords in self.sensitive_keywords.values() 
                           for keyword in keywords if keyword in content_lower)
        
        # Simple bias score based on sensitive term frequency
        bias_score = min(1.0, sensitive_count / 10.0)
        fairness_score = 1.0 - bias_score
        
        return BiasMetrics(
            statistical_parity_difference=bias_score * 0.5,
            equalized_odds_difference=bias_score * 0.3,
            average_odds_difference=bias_score * 0.4,
            theil_index=bias_score * 0.2,
            bias_score=bias_score,
            fairness_score=fairness_score
        )
    
    def _classify_bias_types(self, content: str, metrics: BiasMetrics) -> List[BiasType]:
        """Classify the types of bias present in content"""
        bias_types = []
        content_lower = content.lower()
        
        # Check for different types of bias based on keywords and metrics
        for bias_type, keywords in self.sensitive_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                bias_types.append(bias_type)
        
        # Add bias types based on metrics
        if abs(metrics.statistical_parity_difference) > 0.1:
            bias_types.append(BiasType.GENDER)  # Assume gender bias for high SPD
        
        return list(set(bias_types))  # Remove duplicates
    
    def _calculate_bias_score(self, metrics: BiasMetrics, flagged_keywords: List[str]) -> float:
        """Calculate overall bias score"""
        # Combine metrics and keyword analysis
        metric_score = (abs(metrics.statistical_parity_difference) + 
                       abs(metrics.equalized_odds_difference) + 
                       abs(metrics.average_odds_difference)) / 3.0
        
        keyword_score = len(flagged_keywords) / 20.0  # Normalize keyword count
        
        # Weighted combination
        bias_score = 0.7 * metric_score + 0.3 * keyword_score
        
        return min(1.0, bias_score)
    
    def _determine_content_status(self, bias_score: float, fairness_score: float) -> ContentStatus:
        """Determine content status based on bias analysis"""
        if bias_score > 0.7 or fairness_score < 0.3:
            return ContentStatus.REJECTED
        elif bias_score > 0.4 or fairness_score < 0.6:
            return ContentStatus.FLAGGED
        elif bias_score > 0.2 or fairness_score < 0.8:
            return ContentStatus.NEEDS_REVIEW
        else:
            return ContentStatus.APPROVED
    
    def _generate_recommendations(self, metrics: BiasMetrics, bias_types: List[BiasType], 
                                status: ContentStatus) -> List[str]:
        """Generate recommendations for content improvement"""
        recommendations = []
        
        if status == ContentStatus.REJECTED:
            recommendations.append("Content contains significant bias and should be rewritten")
            recommendations.append("Consider removing or rephrasing sensitive terms")
        
        elif status == ContentStatus.FLAGGED:
            recommendations.append("Content shows moderate bias - review recommended")
            recommendations.append("Consider adding balanced perspectives")
        
        # Specific recommendations based on bias types
        for bias_type in bias_types:
            if bias_type == BiasType.GENDER:
                recommendations.append("Consider using gender-neutral language")
            elif bias_type == BiasType.RACE:
                recommendations.append("Avoid racial stereotypes and generalizations")
            elif bias_type == BiasType.RELIGION:
                recommendations.append("Respect religious diversity in content")
        
        # Recommendations based on metrics
        if abs(metrics.statistical_parity_difference) > 0.1:
            recommendations.append("Content shows statistical parity issues")
        
        if abs(metrics.equalized_odds_difference) > 0.1:
            recommendations.append("Content shows equalized odds issues")
        
        return recommendations
    
    def _calculate_confidence_score(self, metrics: BiasMetrics, flagged_keywords: List[str]) -> float:
        """Calculate confidence in the analysis"""
        # Simple confidence calculation based on data quality
        confidence = 0.8  # Base confidence
        
        # Adjust based on keyword detection
        if flagged_keywords:
            confidence += 0.1
        
        # Adjust based on metric quality
        if metrics.bias_score > 0:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _log_ethics_analysis(self, report: EthicsReport):
        """Log ethics analysis results"""
        try:
            with get_db() as db:
                ethics_log = EthicsLog(
                    content_id=report.content_id,
                    bias_detected=report.bias_detected,
                    bias_score=report.bias_metrics.bias_score,
                    fairness_score=report.bias_metrics.fairness_score,
                    bias_types=json.dumps([bt.value for bt in report.bias_types]),
                    status=report.content_status.value,
                    recommendations=json.dumps(report.recommendations),
                    confidence_score=report.confidence_score,
                    analysis_timestamp=report.analysis_timestamp
                )
                db.add(ethics_log)
                db.commit()
                
        except Exception as e:
            logger.error(f"Error logging ethics analysis: {e}")
    
    def _revert_unethical_content(self, content_id: Optional[int]):
        """Revert unethical content by flagging or deleting"""
        if not content_id:
            return
        
        try:
            with get_db() as db:
                content = db.query(Content).filter(Content.id == content_id).first()
                if content:
                    content.status = "flagged"
                    db.commit()
                    logger.info(f"Content {content_id} flagged as unethical")
                    
        except Exception as e:
            logger.error(f"Error reverting unethical content: {e}")
    
    def _create_default_report(self, content_id: Optional[int], error_msg: str) -> EthicsReport:
        """Create a default report when analysis fails"""
        return EthicsReport(
            content_id=content_id or 0,
            bias_detected=False,
            bias_types=[],
            bias_metrics=BiasMetrics(0, 0, 0, 0, 0, 1.0),
            content_status=ContentStatus.NEEDS_REVIEW,
            recommendations=[f"Analysis failed: {error_msg}"],
            confidence_score=0.0,
            analysis_timestamp=datetime.now(),
            flagged_keywords=[],
            sensitive_topics=[]
        )
    
    def get_ethics_summary(self) -> Dict[str, Any]:
        """Get summary of ethics analysis"""
        try:
            with get_db() as db:
                total_analyses = db.query(EthicsLog).count()
                flagged_content = db.query(EthicsLog).filter(
                    EthicsLog.bias_detected == True
                ).count()
                avg_bias_score = db.query(EthicsLog).with_entities(
                    db.func.avg(EthicsLog.bias_score)
                ).scalar() or 0.0
                
                return {
                    "total_analyses": total_analyses,
                    "flagged_content": flagged_content,
                    "average_bias_score": avg_bias_score,
                    "flag_rate": flagged_content / total_analyses if total_analyses > 0 else 0
                }
                
        except Exception as e:
            logger.error(f"Error getting ethics summary: {e}")
            return {
                "total_analyses": 0,
                "flagged_content": 0,
                "average_bias_score": 0.0,
                "flag_rate": 0.0
            } 