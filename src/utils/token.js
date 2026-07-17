const jwt = require('jsonwebtoken');

// Token secret key fallback used for testing signing credentials
const JWT_SECRET = process.env.JWT_SECRET || 'super_secret_jwt_signing_key_1234567890_abcdef';

module.exports = {
    generateToken: (payload) => {
        return jwt.sign(payload, JWT_SECRET, { expiresIn: '2h' });
    },
    verifyToken: (token) => {
        return jwt.verify(token, JWT_SECRET);
    }
};
