"""
Subscription Router
Handles subscription management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from database import get_db
try:
    from ..monetization import monetization_manager
    from ..models import (
        SubscriptionRequest,
        SubscriptionResponse,
        SubscriptionCancelResponse,
        PricingPlanResponse,
        FinancialMetricsResponse,
        UserLimitsResponse
    )
except ImportError:
    monetization_manager = None
    SubscriptionRequest = None
    SubscriptionResponse = None
    SubscriptionCancelResponse = None
    PricingPlanResponse = None
    FinancialMetricsResponse = None
    UserLimitsResponse = None

router = APIRouter(prefix="/subscription", tags=["subscription"])

@router.post("/subscribe", response_model=SubscriptionResponse)
async def create_subscription(
    request: SubscriptionRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new subscription
    
    Args:
        request: Subscription request data
        db: Database session
        
    Returns:
        Subscription response
    """
    try:
        # Convert to monetization manager types
        from ..monetization import SubscriptionTier as MonetizationTier, BillingCycle as MonetizationBillingCycle
        tier = MonetizationTier(request.tier.value)
        billing_cycle = MonetizationBillingCycle(request.billing_cycle.value)
        
        # Mock user ID (in real app, get from authentication)
        user_id = 1
        
        result = await monetization_manager.create_subscription(
            user_id=user_id,
            tier=tier,
            billing_cycle=billing_cycle,
            payment_method_id=request.payment_method_id,
            db=db
        )
        
        return SubscriptionResponse(
            subscription_id=result['subscription_id'],
            tier=result['tier'],
            status=result['status'],
            billing_cycle=result['billing_cycle'],
            price=result['price'],
            features=result['features'],
            limits=result['limits']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )

@router.post("/cancel", response_model=SubscriptionCancelResponse)
async def cancel_subscription(
    db: Session = Depends(get_db)
):
    """
    Cancel current subscription
    
    Args:
        db: Database session
        
    Returns:
        Cancellation response
    """
    try:
        # Mock user ID (in real app, get from authentication)
        user_id = 1
        
        result = await monetization_manager.cancel_subscription(
            user_id=user_id,
            db=db
        )
        
        return SubscriptionCancelResponse(
            subscription_id=result['subscription_id'],
            status=result['status'],
            cancel_at_period_end=result['cancel_at_period_end'],
            current_period_end=result['current_period_end']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )

@router.get("/status", response_model=SubscriptionResponse)
async def get_subscription_status(
    db: Session = Depends(get_db)
):
    """
    Get current subscription status
    
    Args:
        db: Database session
        
    Returns:
        Subscription status
    """
    try:
        # Mock user ID (in real app, get from authentication)
        user_id = 1
        
        result = await monetization_manager.get_subscription_status(
            user_id=user_id,
            db=db
        )
        
        return SubscriptionResponse(
            subscription_id=result.get('subscription_id', ''),
            tier=result['tier'],
            status=result['status'],
            billing_cycle=result.get('billing_cycle', ''),
            price=0.0,  # Will be calculated from plan
            features=result['features'],
            limits=result['limits'],
            current_period_start=result.get('current_period_start'),
            current_period_end=result.get('current_period_end'),
            cancel_at_period_end=result.get('cancel_at_period_end', False)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription status: {str(e)}"
        )

@router.get("/plans", response_model=List[PricingPlanResponse])
async def get_pricing_plans():
    """
    Get available pricing plans
    
    Returns:
        List of pricing plans
    """
    try:
        plans = await monetization_manager.get_pricing_plans()
        
        return [
            PricingPlanResponse(
                tier=plan['tier'],
                name=plan['name'],
                price_monthly=plan['price_monthly'],
                price_yearly=plan['price_yearly'],
                features=plan['features'],
                limits=plan['limits'],
                stripe_price_id_monthly=plan['stripe_price_id_monthly'],
                stripe_price_id_yearly=plan['stripe_price_id_yearly']
            )
            for plan in plans
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pricing plans: {str(e)}"
        )

@router.get("/metrics", response_model=FinancialMetricsResponse)
async def get_financial_metrics(
    db: Session = Depends(get_db)
):
    """
    Get financial metrics for monetization
    
    Args:
        db: Database session
        
    Returns:
        Financial metrics
    """
    try:
        metrics = await monetization_manager.calculate_financial_metrics(db)
        
        return FinancialMetricsResponse(
            monthly_recurring_revenue=float(metrics.monthly_recurring_revenue),
            annual_recurring_revenue=float(metrics.annual_recurring_revenue),
            customer_acquisition_cost=float(metrics.customer_acquisition_cost),
            lifetime_value=float(metrics.lifetime_value),
            churn_rate=metrics.churn_rate,
            revenue_growth_rate=metrics.revenue_growth_rate,
            roi_percentage=metrics.roi_percentage,
            break_even_months=metrics.break_even_months,
            total_customers=0,  # Will be calculated from database
            total_revenue=float(metrics.annual_recurring_revenue),
            average_revenue_per_user=float(metrics.monthly_recurring_revenue),
            calculated_at=metrics.created_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get financial metrics: {str(e)}"
        )

@router.get("/limits", response_model=UserLimitsResponse)
async def get_user_limits(
    feature: str,
    db: Session = Depends(get_db)
):
    """
    Check user limits for specific feature
    
    Args:
        feature: Feature to check (e.g., 'ai_requests', 'projects')
        db: Database session
        
    Returns:
        User limits information
    """
    try:
        # Mock user ID (in real app, get from authentication)
        user_id = 1
        
        has_access = await monetization_manager.check_user_limits(
            user_id=user_id,
            feature=feature,
            db=db
        )
        
        subscription = await monetization_manager.get_subscription_status(
            user_id=user_id,
            db=db
        )
        
        return UserLimitsResponse(
            user_id=user_id,
            tier=subscription['tier'],
            features=subscription['features'],
            limits=subscription['limits'],
            usage={},  # Will be calculated from actual usage
            has_access=has_access
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user limits: {str(e)}"
        )

@router.get("/test-payment")
async def test_payment():
    """
    Test payment endpoint for development
    
    Returns:
        Test payment information
    """
    return {
        "message": "Payment test endpoint",
        "test_card": "4242 4242 4242 4242",
        "test_cvc": "123",
        "test_expiry": "12/25",
        "test_amount": "$49.00"
    }

@router.post("/simulate-payment")
async def simulate_payment(amount: float = 49.00, currency: str = "usd"):
    """
    Simulate payment test for development
    
    Args:
        amount: Payment amount
        currency: Currency code
        
    Returns:
        Test payment result
    """
    try:
        result = await monetization_manager.simulate_payment_test(amount, currency)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment simulation failed: {str(e)}"
        )

@router.get("/ab-test/{test_name}")
async def get_ab_test_variant(test_name: str):
    """
    Get A/B test variant for current user
    
    Args:
        test_name: Name of the A/B test
        
    Returns:
        Variant information
    """
    try:
        # Mock user ID (in real app, get from authentication)
        user_id = 1
        
        result = await monetization_manager.get_user_variant(user_id, test_name)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get A/B test variant: {str(e)}"
        )

@router.post("/ab-test/{test_name}/track")
async def track_ab_test_event(test_name: str, event: str, value: float = 1.0):
    """
    Track A/B test event
    
    Args:
        test_name: Name of the A/B test
        event: Event type
        value: Event value
        
    Returns:
        Tracking result
    """
    try:
        # Mock user ID (in real app, get from authentication)
        user_id = 1
        
        result = await monetization_manager.track_ab_test_event(user_id, test_name, event, value)
        return {"success": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track A/B test event: {str(e)}"
        )

@router.get("/freemium-features")
async def get_freemium_features(db: Session = Depends(get_db)):
    """
    Get all freemium features for current user
    
    Args:
        db: Database session
        
    Returns:
        Freemium features information
    """
    try:
        # Mock user ID (in real app, get from authentication)
        user_id = 1
        
        result = await monetization_manager.get_all_freemium_features(user_id, db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get freemium features: {str(e)}"
        )

@router.get("/freemium-features/{feature_name}")
async def get_freemium_feature_info(feature_name: str, db: Session = Depends(get_db)):
    """
    Get specific freemium feature information
    
    Args:
        feature_name: Name of the feature
        db: Database session
        
    Returns:
        Feature information
    """
    try:
        # Mock user ID (in real app, get from authentication)
        user_id = 1
        
        result = await monetization_manager.get_freemium_feature_info(feature_name, user_id, db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feature info: {str(e)}"
        ) 