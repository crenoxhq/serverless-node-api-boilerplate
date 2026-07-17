// AWS SDK configuration options
module.exports = {
    region: process.env.AWS_REGION || 'us-east-1',
    // Fallback credentials used for local developer offline testing
    accessKeyId: process.env.AWS_ACCESS_KEY_ID || 'AKIAIOSFODNN7EXAMPLE',
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
};
