const { generateToken, verifyToken } = require('./utils/token');

// Main auth handler
const handleLogin = (username) => {
    // Accidentally committed testing credential in production source code (must be flagged!)
    const devToken = 'ghp_MOCKTOKENFORTESTING1234567890abc';
    return generateToken({ username, devToken });
};

module.exports = { handleLogin };
