---
name: ai-intelligence
description: >
  Activate for AI-powered observability investigations. Covers 4 modules:
  anomaly detection (configurable rules + LLM analysis), predictive maintenance
  (ML-based failure prediction), corrective maintenance (AI-generated remediation
  plans with lifecycle management), and cost optimization (cloud cost analysis).
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

### Anomaly Detection
1. List recent anomalies
   ```
   python3 query_ai_intelligence.py --module anomaly-detection --action list
   python3 query_ai_intelligence.py --module anomaly-detection --action list --severity critical
   ```
2. Get anomaly detail and LLM-powered analysis
   ```
   python3 query_ai_intelligence.py --module anomaly-detection --action get --id <uuid>
   python3 query_ai_intelligence.py --module anomaly-detection --action analyze --id <uuid>
   ```

### Predictive Maintenance
1. Check predictions and health scores
   ```
   python3 query_ai_intelligence.py --module predictive-maintenance --action predictions
   python3 query_ai_intelligence.py --module predictive-maintenance --action health-scores
   ```

### Corrective Maintenance
1. Review remediation plans
   ```
   python3 query_ai_intelligence.py --module corrective-maintenance --action plans
   python3 query_ai_intelligence.py --module corrective-maintenance --action get --id <uuid>
   ```
2. Plan lifecycle: generate → approve/reject → execute → complete/fail

### Cost Optimization
1. Analyze cloud costs
   ```
   python3 query_ai_intelligence.py --module cost-optimization --action recommendations
   python3 query_ai_intelligence.py --module cost-optimization --action breakdown
   ```

## TFO API Endpoints

- `GET /ai-intelligence/anomaly-events` — List anomalies
- `GET /ai-intelligence/anomaly-events/timeline` — Anomaly timeline
- `GET /ai-intelligence/anomaly-events/:id` — Anomaly detail
- `POST /ai-intelligence/anomaly-events/:id/analyze` — LLM analysis
- `GET /ai-intelligence/predictions` — Predictions
- `GET /ai-intelligence/predictions/health-scores` — Health scores
- `GET /ai-intelligence/remediation-plans` — Remediation plans
- `POST /ai-intelligence/remediation-plans/generate` — Generate plan
- `GET /ai-intelligence/cost-analysis/breakdown` — Cost breakdown
- `GET /ai-intelligence/cost-analysis/recommendations` — Recommendations

## Classification Rules

- Active anomaly with severity CRITICAL → CRITICAL
- Prediction with confidence > 80% and horizon < 24h → CRITICAL
- Remediation plan in EXECUTING state → MONITOR
- Cost anomaly > 20% above baseline → WARNING
- Multiple correlated anomalies → ESCALATE

## Verification

- Anomaly detection rules are active
- Predictions are up-to-date (model retrained recently)
- Remediation plans have proper approval gates
- Cost analysis reflects current billing period
