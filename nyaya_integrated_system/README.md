# Nyaya Legal AI - Integrated Production System

## 🎯 Production-Ready Legal Decision Engine

This is the integrated Nyaya Legal AI system combining:
- **Legal Decision Engine** (Raj's datasets & procedures)
- **Sovereign Enforcement Engine** (Chandresh's deterministic governance)
- **RL Feedback System** (Learning & adaptation)
- **API Orchestration** (Nilesh's integration layer)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation & Deployment

1. **Clone and Setup**
```bash
cd nyaya_integrated_system
python deploy.py
```

2. **Manual Setup (Alternative)**
```bash
pip install -r requirements.txt
python main.py
```

3. **Run Tests**
```bash
python test_e2e.py
```

## 📋 API Endpoints

### Core Legal Endpoints
- `POST /api/legal/query` - Single jurisdiction legal query
- `POST /api/legal/multi-jurisdiction` - Multi-jurisdiction comparative analysis
- `POST /api/feedback` - Submit RL feedback
- `GET /api/trace/{trace_id}` - Get audit trail
- `GET /health` - System health check

### Request/Response Examples

**Legal Query:**
```json
{
  "query": "What is the procedure for filing a divorce case?",
  "jurisdiction_hint": "IN",
  "domain_hint": "FAMILY"
}
```

**Response:**
```json
{
  "trace_id": "uuid-here",
  "domain": "FAMILY",
  "jurisdiction": "IN",
  "confidence": 0.85,
  "legal_route": [
    {
      "step": "MEDIATION_ATTEMPT",
      "description": "Facilitated reconciliation",
      "timeline": "30-90 days",
      "evidence_required": ["marriage_certificate"]
    }
  ],
  "enforcement_metadata": {
    "rule_id": "GOVERNANCE_001",
    "policy_source": "GOVERNANCE",
    "reasoning": "Allow legal queries with sufficient confidence",
    "signed_proof": {...}
  }
}
```

## 🔒 Enforcement & Governance

Every request is processed through the Sovereign Enforcement Engine:
- **Deterministic decisions** (ALLOW/BLOCK/ESCALATE)
- **Cryptographic proof** of all decisions
- **Complete audit trail** with trace IDs
- **Policy compliance** validation

## 🧠 RL Learning System

- **Feedback ingestion** with enforcement validation
- **Confidence adjustment** based on user ratings
- **Performance memory** for continuous improvement
- **Learning persistence** across sessions

## 🏗️ System Architecture

```
User Request
     ↓
API Orchestrator
     ↓
Enforcement Engine (Validation)
     ↓
Legal Decision Engine (Processing)
     ↓
RL Engine (Confidence Adjustment)
     ↓
Enforcement Engine (Final Validation)
     ↓
Response with Proof
```

## 📊 Testing & Validation

The system includes comprehensive E2E testing:
- Health checks
- Single & multi-jurisdiction queries
- Feedback submission
- Trace retrieval
- Edge case handling
- Enforcement validation
- RL integration

**Run Tests:**
```bash
python test_e2e.py
```

## 🌐 Production Deployment

**Local Development:**
```bash
python main.py
# Server runs on http://localhost:8000
```

**Production Deployment:**
```bash
python deploy.py
# Configures production environment and starts server
```

## 📈 Monitoring & Health

- **Health Endpoint:** `GET /health`
- **Component Status:** Legal Engine, Enforcement Engine, RL Engine
- **Performance Metrics:** Response times, success rates
- **Audit Logs:** Complete trace of all decisions

## 🔧 Configuration

Environment variables:
- `ENV`: production/development
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

## 📚 Legal Datasets

Integrated datasets from:
- **India:** IPC, CrPC, CPC, Evidence Act, etc.
- **UAE:** Civil Code, Criminal Law, Commercial Law, etc.
- **UK:** Criminal Justice Acts, Civil Procedure Rules, etc.

## 🛡️ Security Features

- **Request validation** through enforcement engine
- **Cryptographic signing** of all decisions
- **Audit trail** for compliance
- **Rate limiting** and security middleware
- **Input sanitization** and validation

## 📋 Production Checklist

✅ **Day 1 Complete:**
- [x] API contracts frozen
- [x] Legal engine wired with datasets
- [x] Enforcement binding implemented
- [x] Single request → response schema

✅ **Day 2 Complete:**
- [x] RL signal & feedback loop
- [x] End-to-end testing suite
- [x] Production deployment ready
- [x] Demo-stable system

## 🎯 Demo Readiness

The system is **DEMO-SAFE** and **NON-FAILING**:
- Comprehensive error handling
- Graceful degradation
- Complete audit trails
- Enforcement cannot be bypassed
- All edge cases handled

## 📞 Support

For issues or questions:
1. Check health endpoint: `/health`
2. Review test results: `test_results.json`
3. Check audit trails: `/api/trace/{trace_id}`

---

**Status:** ✅ Production Ready | Demo Safe | Enforcement Compliant