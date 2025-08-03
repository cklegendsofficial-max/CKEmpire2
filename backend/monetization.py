"""
Monetization Module
Handles Stripe subscriptions, freemium model, and financial metrics
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal

# Stripe imports
try:
    import stripe
    from stripe import Customer, Subscription, Invoice, PaymentMethod
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    logging.warning("Stripe not available. Install with: pip install stripe")

from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from pydantic import BaseModel

from database import get_db
from database import User, Subscription as DBSubscription
from config import settings

logger = logging.getLogger(__name__)

class SubscriptionTier(Enum):
    """Subscription tier enum"""
    FREEMIUM = "freemium"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class BillingCycle(Enum):
    """Billing cycle enum"""
    MONTHLY = "monthly"
    YEARLY = "yearly"

@dataclass
class PricingPlan:
    """Pricing plan configuration"""
    tier: SubscriptionTier
    name: str
    price_monthly: Decimal
    price_yearly: Decimal
    features: List[str]
    limits: Dict[str, int]
    stripe_price_id_monthly: str
    stripe_price_id_yearly: str

@dataclass
class FinancialMetrics:
    """Financial metrics for monetization"""
    monthly_recurring_revenue: Decimal
    annual_recurring_revenue: Decimal
    customer_acquisition_cost: Decimal
    lifetime_value: Decimal
    churn_rate: float
    revenue_growth_rate: float
    roi_percentage: float
    break_even_months: int

class MonetizationManager:
    """Monetization and subscription management"""
    
    def __init__(self):
        self.stripe = None
        self.pricing_plans = {}
        self.financial_metrics = {}
        
        if not STRIPE_AVAILABLE:
            logger.warning("Stripe not available. Using mock responses.")
            return
        
        # Initialize Stripe
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        self.stripe = stripe
        
        # Load pricing plans
        self._load_pricing_plans()
        
        logger.info("Monetization manager initialized")
    
    def _load_pricing_plans(self):
        """Load pricing plans configuration"""
        self.pricing_plans = {
            SubscriptionTier.FREEMIUM: PricingPlan(
                tier=SubscriptionTier.FREEMIUM,
                name="Freemium",
                price_monthly=Decimal('0'),
                price_yearly=Decimal('0'),
                features=[
                    "Temel proje yönetimi",
                    "5 proje limiti",
                    "Temel analitik",
                    "Email desteği"
                ],
                limits={
                    "projects": 5,
                    "ai_requests": 10,
                    "storage_gb": 1,
                    "team_members": 1
                },
                stripe_price_id_monthly="",
                stripe_price_id_yearly=""
            ),
            SubscriptionTier.PREMIUM: PricingPlan(
                tier=SubscriptionTier.PREMIUM,
                name="Premium",
                price_monthly=Decimal('49'),
                price_yearly=Decimal('490'),
                features=[
                    "Sınırsız proje",
                    "AI destekli strateji",
                    "Gelişmiş analitik",
                    "Öncelikli destek",
                    "Video üretimi",
                    "NFT entegrasyonu"
                ],
                limits={
                    "projects": -1,  # Unlimited
                    "ai_requests": 1000,
                    "storage_gb": 50,
                    "team_members": 10
                },
                stripe_price_id_monthly=os.getenv('STRIPE_PREMIUM_MONTHLY_PRICE_ID', ''),
                stripe_price_id_yearly=os.getenv('STRIPE_PREMIUM_YEARLY_PRICE_ID', '')
            ),
            SubscriptionTier.ENTERPRISE: PricingPlan(
                tier=SubscriptionTier.ENTERPRISE,
                name="Enterprise",
                price_monthly=Decimal('199'),
                price_yearly=Decimal('1990'),
                features=[
                    "Tüm Premium özellikler",
                    "Özel AI modelleri",
                    "API erişimi",
                    "Dedicated support",
                    "Custom integrations",
                    "White-label çözümler"
                ],
                limits={
                    "projects": -1,
                    "ai_requests": -1,
                    "storage_gb": 500,
                    "team_members": -1
                },
                stripe_price_id_monthly=os.getenv('STRIPE_ENTERPRISE_MONTHLY_PRICE_ID', ''),
                stripe_price_id_yearly=os.getenv('STRIPE_ENTERPRISE_YEARLY_PRICE_ID', '')
            )
        }
        
        logger.info(f"Loaded {len(self.pricing_plans)} pricing plans")
    
    async def create_subscription(self, user_id: int, tier: SubscriptionTier, 
                                billing_cycle: BillingCycle, payment_method_id: str,
                                db: Session) -> Dict[str, Any]:
        """
        Create Stripe subscription
        
        Args:
            user_id: User ID
            tier: Subscription tier
            billing_cycle: Billing cycle
            payment_method_id: Stripe payment method ID
            db: Database session
            
        Returns:
            Dict with subscription information
        """
        try:
            if not STRIPE_AVAILABLE:
                logger.warning("Stripe not available. Using mock subscription creation.")
                return self._create_mock_subscription(user_id, tier, billing_cycle)
            
            # Get user
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get pricing plan
            plan = self.pricing_plans.get(tier)
            if not plan:
                raise HTTPException(status_code=400, detail="Invalid subscription tier")
            
            # Get Stripe price ID
            price_id = (plan.stripe_price_id_yearly if billing_cycle == BillingCycle.YEARLY 
                       else plan.stripe_price_id_monthly)
            
            if not price_id:
                raise HTTPException(status_code=400, detail="Price ID not configured")
            
            # Create or get Stripe customer
            customer = await self._get_or_create_stripe_customer(user)
            
            # Attach payment method to customer
            self.stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer.id
            )
            
            # Set as default payment method
            self.stripe.Customer.modify(
                customer.id,
                invoice_settings={'default_payment_method': payment_method_id}
            )
            
            # Create subscription
            subscription = self.stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': price_id}],
                payment_behavior='default_incomplete',
                payment_settings={'save_default_payment_method': 'on_subscription'},
                expand=['latest_invoice.payment_intent']
            )
            
            # Save to database
            db_subscription = DBSubscription(
                user_id=user_id,
                stripe_subscription_id=subscription.id,
                tier=tier.value,
                billing_cycle=billing_cycle.value,
                status=subscription.status,
                current_period_start=datetime.fromtimestamp(subscription.current_period_start),
                current_period_end=datetime.fromtimestamp(subscription.current_period_end),
                cancel_at_period_end=subscription.cancel_at_period_end
            )
            db.add(db_subscription)
            db.commit()
            
            logger.info(f"Created subscription for user {user_id}: {subscription.id}")
            
            return {
                'subscription_id': subscription.id,
                'status': subscription.status,
                'tier': tier.value,
                'billing_cycle': billing_cycle.value,
                'price': float(plan.price_monthly if billing_cycle == BillingCycle.MONTHLY else plan.price_yearly),
                'features': plan.features,
                'limits': plan.limits
            }
            
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            raise HTTPException(status_code=500, detail=f"Subscription creation failed: {str(e)}")
    
    async def _get_or_create_stripe_customer(self, user: User) -> Customer:
        """Get or create Stripe customer for user"""
        try:
            # Check if user already has Stripe customer ID
            if user.stripe_customer_id:
                return self.stripe.Customer.retrieve(user.stripe_customer_id)
            
            # Create new customer
            customer = self.stripe.Customer.create(
                email=user.email,
                name=user.full_name,
                metadata={
                    'user_id': str(user.id),
                    'created_at': user.created_at.isoformat()
                }
            )
            
            # Update user with Stripe customer ID
            user.stripe_customer_id = customer.id
            user.db.commit()
            
            return customer
            
        except Exception as e:
            logger.error(f"Failed to get/create Stripe customer: {e}")
            raise
    
    async def cancel_subscription(self, user_id: int, db: Session) -> Dict[str, Any]:
        """
        Cancel Stripe subscription
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            Dict with cancellation information
        """
        try:
            if not STRIPE_AVAILABLE:
                logger.warning("Stripe not available. Using mock subscription cancellation.")
                return self._create_mock_cancellation(user_id)
            
            # Get user subscription
            subscription = db.query(DBSubscription).filter(
                DBSubscription.user_id == user_id,
                DBSubscription.status.in_(['active', 'trialing'])
            ).first()
            
            if not subscription:
                raise HTTPException(status_code=404, detail="Active subscription not found")
            
            # Cancel Stripe subscription
            stripe_subscription = self.stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )
            
            # Update database
            subscription.status = stripe_subscription.status
            subscription.cancel_at_period_end = True
            db.commit()
            
            logger.info(f"Cancelled subscription for user {user_id}: {subscription.stripe_subscription_id}")
            
            return {
                'subscription_id': subscription.stripe_subscription_id,
                'status': subscription.status,
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'current_period_end': subscription.current_period_end.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {e}")
            raise HTTPException(status_code=500, detail=f"Subscription cancellation failed: {str(e)}")
    
    async def get_subscription_status(self, user_id: int, db: Session) -> Dict[str, Any]:
        """
        Get subscription status for user
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            Dict with subscription status
        """
        try:
            subscription = db.query(DBSubscription).filter(
                DBSubscription.user_id == user_id
            ).first()
            
            if not subscription:
                return {
                    'has_subscription': False,
                    'tier': SubscriptionTier.FREEMIUM.value,
                    'status': 'inactive',
                    'features': self.pricing_plans[SubscriptionTier.FREEMIUM].features,
                    'limits': self.pricing_plans[SubscriptionTier.FREEMIUM].limits
                }
            
            # Get current plan
            plan = self.pricing_plans.get(SubscriptionTier(subscription.tier))
            
            return {
                'has_subscription': True,
                'subscription_id': subscription.stripe_subscription_id,
                'tier': subscription.tier,
                'status': subscription.status,
                'billing_cycle': subscription.billing_cycle,
                'current_period_start': subscription.current_period_start.isoformat(),
                'current_period_end': subscription.current_period_end.isoformat(),
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'features': plan.features if plan else [],
                'limits': plan.limits if plan else {}
            }
            
        except Exception as e:
            logger.error(f"Failed to get subscription status: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get subscription status: {str(e)}")
    
    async def calculate_financial_metrics(self, db: Session) -> FinancialMetrics:
        """
        Calculate financial metrics for monetization
        
        Args:
            db: Database session
            
        Returns:
            FinancialMetrics object
        """
        try:
            # Get subscription data
            active_subscriptions = db.query(DBSubscription).filter(
                DBSubscription.status.in_(['active', 'trialing'])
            ).all()
            
            # Calculate MRR (Monthly Recurring Revenue)
            mrr = Decimal('0')
            for sub in active_subscriptions:
                plan = self.pricing_plans.get(SubscriptionTier(sub.tier))
                if plan:
                    if sub.billing_cycle == BillingCycle.MONTHLY.value:
                        mrr += plan.price_monthly
                    else:  # Yearly
                        mrr += plan.price_yearly / 12
            
            # Calculate ARR (Annual Recurring Revenue)
            arr = mrr * 12
            
            # Mock CAC and LTV calculations (in real scenario, these would come from analytics)
            cac = Decimal('25')  # Customer Acquisition Cost
            ltv = mrr * 24  # Lifetime Value (2 years average)
            
            # Calculate churn rate (mock)
            total_subscriptions = len(active_subscriptions)
            cancelled_this_month = db.query(DBSubscription).filter(
                DBSubscription.status == 'canceled',
                DBSubscription.updated_at >= datetime.utcnow() - timedelta(days=30)
            ).count()
            
            churn_rate = (cancelled_this_month / max(total_subscriptions, 1)) * 100
            
            # Calculate ROI
            roi_percentage = ((ltv - cac) / cac) * 100 if cac > 0 else 0
            
            # Calculate break-even months
            break_even_months = int(cac / mrr) if mrr > 0 else 0
            
            # Calculate growth rate (mock)
            last_month_subscriptions = db.query(DBSubscription).filter(
                DBSubscription.created_at >= datetime.utcnow() - timedelta(days=60),
                DBSubscription.created_at < datetime.utcnow() - timedelta(days=30)
            ).count()
            
            growth_rate = ((total_subscriptions - last_month_subscriptions) / max(last_month_subscriptions, 1)) * 100
            
            metrics = FinancialMetrics(
                monthly_recurring_revenue=mrr,
                annual_recurring_revenue=arr,
                customer_acquisition_cost=cac,
                lifetime_value=ltv,
                churn_rate=churn_rate,
                revenue_growth_rate=growth_rate,
                roi_percentage=roi_percentage,
                break_even_months=break_even_months
            )
            
            self.financial_metrics = metrics
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate financial metrics: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to calculate financial metrics: {str(e)}")
    
    async def get_pricing_plans(self) -> List[Dict[str, Any]]:
        """
        Get available pricing plans
        
        Returns:
            List of pricing plans
        """
        plans = []
        for tier, plan in self.pricing_plans.items():
            plans.append({
                'tier': tier.value,
                'name': plan.name,
                'price_monthly': float(plan.price_monthly),
                'price_yearly': float(plan.price_yearly),
                'features': plan.features,
                'limits': plan.limits,
                'stripe_price_id_monthly': plan.stripe_price_id_monthly,
                'stripe_price_id_yearly': plan.stripe_price_id_yearly
            })
        
        return plans
    
    def _create_mock_subscription(self, user_id: int, tier: SubscriptionTier, 
                                 billing_cycle: BillingCycle) -> Dict[str, Any]:
        """Create mock subscription for testing"""
        plan = self.pricing_plans.get(tier)
        return {
            'subscription_id': f'mock_sub_{user_id}_{tier.value}',
            'status': 'active',
            'tier': tier.value,
            'billing_cycle': billing_cycle.value,
            'price': float(plan.price_monthly if billing_cycle == BillingCycle.MONTHLY else plan.price_yearly),
            'features': plan.features,
            'limits': plan.limits
        }
    
    def _create_mock_cancellation(self, user_id: int) -> Dict[str, Any]:
        """Create mock cancellation for testing"""
        return {
            'subscription_id': f'mock_sub_{user_id}_premium',
            'status': 'active',
            'cancel_at_period_end': True,
            'current_period_end': (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
    
    async def check_user_limits(self, user_id: int, feature: str, db: Session) -> bool:
        """
        Check if user has access to feature based on subscription limits
        
        Args:
            user_id: User ID
            feature: Feature to check (e.g., 'ai_requests', 'projects')
            db: Database session
            
        Returns:
            bool: True if user has access
        """
        try:
            subscription = await self.get_subscription_status(user_id, db)
            
            if not subscription['has_subscription']:
                # Freemium user
                limits = self.pricing_plans[SubscriptionTier.FREEMIUM].limits
            else:
                # Paid user
                tier = SubscriptionTier(subscription['tier'])
                limits = self.pricing_plans[tier].limits
            
            # Check if feature has unlimited access
            if feature in limits and limits[feature] == -1:
                return True
            
            # For now, return True (in real implementation, you'd check actual usage)
            return True
            
        except Exception as e:
            logger.error(f"Failed to check user limits: {e}")
            return False

# Global instance
monetization_manager = MonetizationManager() 