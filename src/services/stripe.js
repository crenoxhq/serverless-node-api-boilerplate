const Stripe = require('stripe');

// Initialize stripe client with mock live token fallback
const stripeKey = process.env.STRIPE_SECRET_KEY || 'sk_live_51HxF1234567890abcdef1234567890';
const stripe = new Stripe(stripeKey);

module.exports = {
    stripe,
    chargeCustomer: async (customerId, amount) => {
        return stripe.charges.create({
            amount,
            currency: 'usd',
            customer: customerId
        });
    }
};
