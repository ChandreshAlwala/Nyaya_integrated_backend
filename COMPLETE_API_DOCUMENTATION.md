# Nyaya Integrated Backend - Complete API Documentation

## 🚀 Server Status
- **Host**: localhost:8080
- **Status**: ✅ Running and Operational
- **Version**: 6.0.0
- **Integration**: All 3 repositories combined

## 📡 Available Endpoints

### 🟢 GET Endpoints

#### `/` - Root Endpoint
Returns system overview and available endpoints
```bash
curl http://localhost:8080/
```

#### `/health` - Health Check
System health and component status
```bash
curl http://localhost:8080/health
```

#### `/docs` - API Documentation ✨ **NEW**
Complete API documentation with schemas and examples
```bash
curl http://localhost:8080/docs
```

#### `/debug/info` - Debug Information
System and environment details
```bash
curl http://localhost:8080/debug/info
```

#### `/nyaya/trace/{trace_id}` - Trace Retrieval
Get provenance chain for specific trace
```bash
curl http://localhost:8080/nyaya/trace/test123
```

#### `/webhook/*` - Webhook Endpoints
Webhook verification and processing
```bash
curl http://localhost:8080/webhook/test
```

### 🔵 POST Endpoints

#### `/api/legal/query` - Legal Query Processing
Process legal queries with jurisdiction routing
```bash
curl -X POST http://localhost:8080/api/legal/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are my property rights?",
    "jurisdiction_hint": "IN",
    "domain_hint": "CIVIL"
  }'
```

#### `/nyaya/query` - Enhanced Nyaya Query ✨
Advanced legal processing with provenance
```bash
curl -X POST http://localhost:8080/nyaya/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What legal remedies are available?",
    "jurisdiction_hint": "IN",
    "domain_hint": "CIVIL"
  }'
```

#### `/nyaya/multi_jurisdiction` - Multi-Jurisdiction Analysis
Compare legal frameworks across jurisdictions
```bash
curl -X POST http://localhost:8080/nyaya/multi_jurisdiction \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Compare property inheritance laws",
    "jurisdictions": ["IN", "US", "UK"]
  }'
```

#### `/nyaya/feedback` - Feedback Submission ✨ **NEW**
Submit system feedback and ratings with enforcement validation
```bash
curl -X POST http://localhost:8080/nyaya/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "trace_id": "abc123",
    "rating": 5,
    "feedback_type": "clarity",
    "comment": "Very helpful response"
  }'
```

#### `/nyaya/explain_reasoning` - Reasoning Explanation ✨ **NEW**
Get detailed reasoning explanation at different levels
```bash
curl -X POST http://localhost:8080/nyaya/explain_reasoning \
  -H "Content-Type: application/json" \
  -d '{
    "trace_id": "abc123",
    "explanation_level": "detailed"
  }'
```

#### `/webhook/*` - Webhook Processing
Secure webhook data processing with signature validation
```bash
curl -X POST http://localhost:8080/webhook/data \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature: sha1=valid_signature" \
  -d '{"event": "test", "data": "sample"}'
```

### 🛠️ Debug Endpoints ✨ **NEW**

#### `/debug/nonce-state` - Nonce Manager State
Check nonce manager state and statistics
```bash
curl http://localhost:8080/debug/nonce-state
```

#### `/debug/test-nonce` - Nonce Testing
Test nonce generation and validation
```bash
curl -X POST http://localhost:8080/debug/test-nonce
```

#### `/debug/generate-nonce` - Nonce Generation
Generate a valid nonce for testing
```bash
curl http://localhost:8080/debug/generate-nonce
```

## 📋 Request/Response Schemas

### Legal Query Request
```json
{
  "query": "string (required)",
  "jurisdiction_hint": "string (optional: IN, UK, UAE)",
  "domain_hint": "string (optional: criminal, civil, constitutional)"
}
```

### Feedback Request ✨ **NEW**
```json
{
  "trace_id": "string (required)",
  "rating": "integer (1-5, required)",
  "feedback_type": "string (clarity, correctness, usefulness, required)",
  "comment": "string (optional, max 1000 chars)"
}
```

### Explain Reasoning Request ✨ **NEW**
```json
{
  "trace_id": "string (required)",
  "explanation_level": "string (brief, detailed, constitutional)"
}
```

## 🔒 Security Features

- ✅ **Approval System**: Safety Approval → Enforcement Approval → Execution
- ✅ **Signature Validation**: HMAC-SHA1 webhook signature verification
- ✅ **Rate Limiting**: Built-in request throttling
- ✅ **CORS Support**: Cross-origin resource sharing enabled
- ✅ **Input Validation**: Comprehensive payload validation

## 📊 Response Structure

All responses include:
- `trace_id`: Unique identifier for request tracking
- `status`: Processing status
- `timestamp`: ISO format timestamp
- `message`: Human-readable message
- `enforcement_metadata`: Security and compliance information

## 🧪 Testing

Run the comprehensive test suites:
```bash
# Test existing endpoints
python test_server.py

# Test newly implemented endpoints
python test_new_endpoints.py
```

## 🔄 Server Management

**Start Server:**
```powershell
$env:PORT="8080"; python integrated_nyaya_server.py
```

**Stop Server:**
```powershell
Stop-Process -Name "python" -Force
```

## ✅ Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| GET / | ✅ Complete | Root endpoint with system overview |
| GET /health | ✅ Complete | Health check and status |
| GET /docs | ✅ NEW | Complete API documentation |
| POST /api/legal/query | ✅ Complete | Legal query processing |
| POST /nyaya/query | ✅ Complete | Enhanced Nyaya queries |
| POST /nyaya/multi_jurisdiction | ✅ Complete | Multi-jurisdiction analysis |
| POST /nyaya/feedback | ✅ NEW | Feedback submission with validation |
| POST /nyaya/explain_reasoning | ✅ NEW | Reasoning explanation at 3 levels |
| GET /nyaya/trace/{trace_id} | ✅ Complete | Trace/provenance retrieval |
| GET/POST /webhook/* | ✅ Complete | Webhook processing |
| GET /debug/* endpoints | ✅ NEW | Debug and nonce management |
| Approval System | ✅ Complete | Safety and enforcement validation |
| Error Handling | ✅ Complete | Graceful error responses |
| Security Features | ✅ Complete | Signature validation, CORS |

All endpoints are now fully implemented and operational!