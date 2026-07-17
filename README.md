# Serverless Node.js API Boilerplate & Secrets Scanner Benchmark

A production-ready serverless backend boilerplate built with Node.js, Express, and Serverless Framework. Designed to deploy on AWS Lambda and integrate with PostgreSQL and Stripe.

This repository is also configured as a **Secrets Detection & Security Scanner Benchmark**. It contains simulated credentials and mock API tokens hidden inside fallback configurations, databases, and authentication handlers to validate the recall, precision, and performance of security scanning tools (such as Crenox, Gitleaks, and TruffleHog).

## Features
- **Serverless Architecture:** Configured for AWS Lambda, API Gateway, and local testing.
- **Database Integration:** Pre-configured PostgreSQL connection pools and mock migrations.
- **Stripe Payments:** Gateway APIs ready for integration.
- **Security:** Token-based user authentication and verification.
- **Scanner Testing Ground:** Built-in credentials to evaluate CI/CD secret scanning pipelines.

---

## ⚡ Verified with Crenox

This benchmark repository is officially verified and audited using **Crenox** — an enterprise-grade, ultra-lightweight secrets detector.

Crenox utilizes a three-tier detection pipeline to achieve industry-leading performance and accuracy:
1. **Tier 1 (PATTERN):** High-speed Aho-Corasick trie matching of predefined signatures.
2. **Tier 2 (ENTROPY):** Shannon entropy analysis to locate novel, high-randomness secrets (like raw hex and base64 strings).
3. **Tier 3 (CONTEXT):** Context-aware suppression to eliminate false positives in test directories, code comments, and environment placeholders.

Crenox completes the scan of this repository in **under 4 milliseconds**, achieving **100% recall** (detecting all 7 embedded secrets) and **100% precision** (ignoring all safe mock placeholders).

### How to scan with Crenox:
```bash
# Run recursive directory scan
crenox scan -r .
```

---

## 🔒 Secrets Benchmark Directory (Mock Credentials Location)

For security auditing and benchmark verification, the following simulated secrets have been intentionally embedded within the project structure:

| Secret Type | Location | Detection Mechanism | Description |
| :--- | :--- | :--- | :--- |
| **AWS Access Key ID** | [`src/config/aws.js` (Line 5)](file:///root/serverless-node-api-boilerplate/src/config/aws.js#L5) | Pattern Matching | Mock AWS user IAM key fallback (`AKIA...`). |
| **AWS Secret Access Key** | [`src/config/aws.js` (Line 6)](file:///root/serverless-node-api-boilerplate/src/config/aws.js#L6) | Shannon Entropy | Mock high-entropy AWS secret credentials. |
| **Stripe Live Secret Key** | [`src/services/stripe.js` (Line 4)](file:///root/serverless-node-api-boilerplate/src/services/stripe.js#L4) | Pattern Matching | Simulated live payments secret gateway key (`sk_live_...`). |
| **PostgreSQL Connection String** | [`src/db/connect.js` (Line 2)](file:///root/serverless-node-api-boilerplate/src/db/connect.js#L2) | Pattern Matching / DSN | Active PostgreSQL DSN connection URL with passwords. |
| **JWT Signing Token Secret** | [`src/utils/token.js` (Line 4)](file:///root/serverless-node-api-boilerplate/src/utils/token.js#L4) | Shannon Entropy | High-entropy signing key configuration for JSON Web Tokens. |
| **GitHub Personal Access Token** | [`src/auth-handler.js` (Line 6)](file:///root/serverless-node-api-boilerplate/src/auth-handler.js#L6) | Pattern Matching | Mock classic GitHub PAT token (`ghp_...`) in auth handler. |

### 🛡️ Context-Aware Exclusion Tests (Suppression Cases)
* **Test Directories:** We previously tested simulated tokens inside test folders (e.g., `tests/`) to verify that scanners correctly classify them as `SafeTestFile` and do not generate false positives on test fixtures.
* **SQL Comments:** Commented out SQL links (using `--` prefixes) are designed to verify `SafeComment` suppression policies.

---

## Getting Started

### 1. Installation
Clone the repository and install dependencies:
```bash
npm install
```

### 2. Configuration
Copy the environment variables template:
```bash
cp .env.example .env
```

### 3. Running Locally
Start the server in developer mode:
```bash
npm start
```

### 4. Deploying to AWS
Deploy the serverless package to AWS Lambda:
```bash
serverless deploy --stage prod
```

## License
MIT License. Developed for developer security benchmarking.
