import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SubscriptionButton.css';

const SubscriptionButton = ({ userTier = 'freemium', onSubscriptionChange }) => {
    const [loading, setLoading] = useState(false);
    const [subscriptionStatus, setSubscriptionStatus] = useState(null);
    const [pricingPlans, setPricingPlans] = useState([]);
    const [showPricingModal, setShowPricingModal] = useState(false);
    const [selectedPlan, setSelectedPlan] = useState(null);
    const [billingCycle, setBillingCycle] = useState('monthly');
    const [abTestVariant, setAbTestVariant] = useState(null);
    const [freemiumFeatures, setFreemiumFeatures] = useState({});

    useEffect(() => {
        fetchSubscriptionStatus();
        fetchPricingPlans();
        fetchAbTestVariant();
        fetchFreemiumFeatures();
    }, []);

    const fetchSubscriptionStatus = async () => {
        try {
            const response = await axios.get('/api/v1/subscription/status');
            setSubscriptionStatus(response.data);
        } catch (error) {
            console.error('Failed to fetch subscription status:', error);
        }
    };

    const fetchPricingPlans = async () => {
        try {
            const response = await axios.get('/api/v1/subscription/plans');
            setPricingPlans(response.data);
        } catch (error) {
            console.error('Failed to fetch pricing plans:', error);
        }
    };

    const fetchAbTestVariant = async () => {
        try {
            const response = await axios.get('/api/v1/subscription/ab-test/pricing_page');
            setAbTestVariant(response.data);
        } catch (error) {
            console.error('Failed to fetch A/B test variant:', error);
        }
    };

    const fetchFreemiumFeatures = async () => {
        try {
            const response = await axios.get('/api/v1/subscription/freemium-features');
            setFreemiumFeatures(response.data);
        } catch (error) {
            console.error('Failed to fetch freemium features:', error);
        }
    };

    const handleSubscribe = async (plan) => {
        setLoading(true);
        try {
            // Track A/B test conversion event
            if (abTestVariant?.test_active) {
                await axios.post(`/api/v1/subscription/ab-test/pricing_page/track`, {
                    event: 'conversion',
                    value: 1.0
                });
            }

            // In a real app, you would integrate with Stripe Elements
            // For now, we'll use a mock payment method
            const mockPaymentMethod = 'pm_test_1234567890';
            
            const response = await axios.post('/api/v1/subscription/subscribe', {
                tier: plan.tier,
                billing_cycle: billingCycle,
                payment_method_id: mockPaymentMethod
            });

            setSubscriptionStatus(response.data);
            setShowPricingModal(false);
            onSubscriptionChange?.(response.data);
            
            // Show success message
            alert(`Successfully subscribed to ${plan.name}!`);
        } catch (error) {
            console.error('Failed to subscribe:', error);
            alert('Failed to subscribe. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleCancelSubscription = async () => {
        if (!confirm('Are you sure you want to cancel your subscription?')) {
            return;
        }

        setLoading(true);
        try {
            const response = await axios.post('/api/v1/subscription/cancel');
            setSubscriptionStatus(response.data);
            onSubscriptionChange?.(response.data);
            alert('Subscription cancelled successfully.');
        } catch (error) {
            console.error('Failed to cancel subscription:', error);
            alert('Failed to cancel subscription. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const getCurrentPlan = () => {
        if (!subscriptionStatus) return null;
        return pricingPlans.find(plan => plan.tier === subscriptionStatus.tier);
    };

    const currentPlan = getCurrentPlan();

    return (
        <div className="subscription-container">
            {/* Current Subscription Status */}
            <div className="subscription-status">
                <h3>Current Plan: {currentPlan?.name || 'Freemium'}</h3>
                {subscriptionStatus && (
                    <div className="status-details">
                        <p>Status: <span className={`status ${subscriptionStatus.status}`}>
                            {subscriptionStatus.status}
                        </span></p>
                        {subscriptionStatus.billing_cycle && (
                            <p>Billing: {subscriptionStatus.billing_cycle}</p>
                        )}
                        {subscriptionStatus.current_period_end && (
                            <p>Next billing: {new Date(subscriptionStatus.current_period_end).toLocaleDateString()}</p>
                        )}
                    </div>
                )}
            </div>

            {/* Action Buttons */}
            <div className="subscription-actions">
                {subscriptionStatus?.has_subscription ? (
                    <button 
                        className="btn-cancel"
                        onClick={handleCancelSubscription}
                        disabled={loading}
                    >
                        {loading ? 'Cancelling...' : 'Cancel Subscription'}
                    </button>
                ) : (
                    <button 
                        className="btn-upgrade"
                        onClick={() => setShowPricingModal(true)}
                        disabled={loading}
                    >
                        Upgrade to Premium
                    </button>
                )}
            </div>

            {/* Pricing Modal */}
            {showPricingModal && (
                <div className="modal-overlay" onClick={() => setShowPricingModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Choose Your Plan</h2>
                            <button 
                                className="modal-close"
                                onClick={() => setShowPricingModal(false)}
                            >
                                ×
                            </button>
                        </div>

                        <div className="billing-toggle">
                            <label>
                                <input
                                    type="radio"
                                    value="monthly"
                                    checked={billingCycle === 'monthly'}
                                    onChange={(e) => setBillingCycle(e.target.value)}
                                />
                                Monthly
                            </label>
                            <label>
                                <input
                                    type="radio"
                                    value="yearly"
                                    checked={billingCycle === 'yearly'}
                                    onChange={(e) => setBillingCycle(e.target.value)}
                                />
                                Yearly (Save 17%)
                            </label>
                        </div>

                        <div className="pricing-plans">
                            {pricingPlans.map((plan) => (
                                <div key={plan.tier} className={`plan-card ${plan.tier}`}>
                                    <div className="plan-header">
                                        <h3>{plan.name}</h3>
                                        <div className="plan-price">
                                            <span className="currency">$</span>
                                            <span className="amount">
                                                {billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly}
                                            </span>
                                            <span className="period">
                                                /{billingCycle === 'monthly' ? 'month' : 'year'}
                                            </span>
                                        </div>
                                    </div>

                                    <div className="plan-features">
                                        <ul>
                                            {plan.features.map((feature, index) => (
                                                <li key={index}>✓ {feature}</li>
                                            ))}
                                        </ul>
                                    </div>

                                    <div className="plan-limits">
                                        <h4>Limits:</h4>
                                        <ul>
                                            {Object.entries(plan.limits).map(([key, value]) => (
                                                <li key={key}>
                                                    {key.replace('_', ' ')}: {value === -1 ? 'Unlimited' : value}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    <button
                                        className={`btn-subscribe ${plan.tier}`}
                                        onClick={() => handleSubscribe(plan)}
                                        disabled={loading}
                                    >
                                        {loading ? 'Processing...' : `Subscribe to ${plan.name}`}
                                    </button>
                                </div>
                            ))}
                        </div>

                        <div className="modal-footer">
                            <p className="test-info">
                                💳 Test Card: 4242 4242 4242 4242 | CVC: 123 | Expiry: 12/25
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* Features List */}
            {currentPlan && (
                <div className="current-features">
                    <h4>Your Features:</h4>
                    <ul>
                        {currentPlan.features.map((feature, index) => (
                            <li key={index}>✓ {feature}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Freemium Features Display */}
            {freemiumFeatures.features && (
                <div className="freemium-features">
                    <h4>Feature Access:</h4>
                    <div className="features-grid">
                        {Object.entries(freemiumFeatures.features).map(([featureName, feature]) => (
                            <div key={featureName} className={`feature-item ${feature.available ? 'available' : 'locked'}`}>
                                <div className="feature-header">
                                    <h5>{featureName.replace('_', ' ').toUpperCase()}</h5>
                                    <span className={`status ${feature.available ? 'available' : 'locked'}`}>
                                        {feature.available ? '✓ Available' : '🔒 Locked'}
                                    </span>
                                </div>
                                <p className="feature-description">{feature.description}</p>
                                <div className="feature-limits">
                                    <span>Limit: {feature.unlimited ? 'Unlimited' : feature.current_limit}</span>
                                </div>
                                {!feature.available && feature.upgrade_prompt && (
                                    <div className="upgrade-prompt">
                                        <p>{feature.upgrade_prompt}</p>
                                        <button 
                                            className="btn-upgrade-feature"
                                            onClick={() => setShowPricingModal(true)}
                                        >
                                            Upgrade Now
                                        </button>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* A/B Test Info (for debugging) */}
            {abTestVariant?.test_active && (
                <div className="ab-test-info">
                    <small>🧪 A/B Test Active: Variant {abTestVariant.variant}</small>
                </div>
            )}
        </div>
    );
};

export default SubscriptionButton; 