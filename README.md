# 🎓 Universal Front Door Support Agent

> **Eliminating the "47 Front Doors" Problem in University Support**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4+-06B6D4?style=flat&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Development Status](#-development-status)
- [Version Compatibility](#-version-compatibility)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

---

## 🌟 Overview

The **Universal Front Door Support Agent** is a three-agent AI system that provides a single, intelligent entry point for all university student support requests. Instead of navigating multiple disconnected support channels, students interact with one interface that:

- 🎯 **Detects intent** from natural language queries
- 🔀 **Routes requests** to the correct department
- 🎫 **Creates tickets** automatically in ServiceNow
- 📚 **Retrieves knowledge** articles for self-service
- 👤 **Escalates to humans** for policy-related requests

**Target Impact**: Increase first-contact resolution from **40%** to **65%**

---

## 🚨 Problem Statement

Universities suffer from a fragmented support experience:

| Issue | Current State | Impact |
|-------|---------------|--------|
| 🚪 Multiple Entry Points | "47 front doors" | Students don't know where to go |
| 🔄 Transfer Rate | 3+ transfers average | Students re-explain issues repeatedly |
| ⏱️ Wait Times | >20 minutes | Poor student experience |
| 🌙 After-Hours | No coverage | Requests go unanswered |
| ✅ First-Contact Resolution | 40% | Low efficiency |

---

## ✨ Features

### 🤖 Intelligent Routing
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   QueryAgent    │───▶│   RouterAgent   │───▶│   ActionAgent   │
│                 │    │                 │    │                 │
│ • Intent detect │    │ • Route decision│    │ • Create ticket │
│ • Entity extract│    │ • Escalation    │    │ • Retrieve KB   │
│ • PII detection │    │ • Priority set  │    │ • Send response │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🏢 Department Support

| Department | Intent Examples |
|------------|-----------------|
| 💻 IT | Password reset, account locked, VPN issues |
| 📋 Registrar | Transcript request, enrollment verification |
| 💰 Financial Aid | FAFSA questions, scholarship inquiry |
| 🏗️ Facilities | Maintenance request, room booking |
| 👥 HR | Employment verification, payroll questions |
| 🎓 Student Affairs | Housing, student organizations |
| 🚔 Campus Safety | Parking permits, safety concerns |

### 🚨 Smart Escalation Triggers

```
┌────────────────────────────────────────────────────────────┐
│                    ESCALATION TRIGGERS                     │
├────────────────────────────────────────────────────────────┤
│ ⚠️  Confidence score < 0.70                                │
│ 📜 Policy keywords: appeal, waiver, refund, exception      │
│ 🚨 Sensitive topics: Title IX, mental health, threats      │
│ 🔀 Multi-department coordination needed                    │
│ 👤 User explicitly requests human                          │
│ ❓ 3 failed clarification attempts                         │
└────────────────────────────────────────────────────────────┘
```

### ♿ Accessibility (WCAG AA Compliant)

- 🔲 High contrast mode toggle
- ⌨️ Full keyboard navigation
- 🏷️ ARIA labels throughout
- 📱 Mobile responsive design
- 🔗 Skip navigation links

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                           FRONTEND                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           React 18 + TypeScript + Tailwind               │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────────┐   │   │
│  │  │ Header │ │  Chat  │ │ Ticket │ │ Knowledge      │   │   │
│  │  │        │ │Container│ │  Card  │ │ Article List   │   │   │
│  │  └────────┘ └────────┘ └────────┘ └────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼ REST API
┌──────────────────────────────────────────────────────────────────┐
│                           BACKEND                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    FastAPI + Python 3.11                  │   │
│  │                                                           │   │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐    │   │
│  │  │ QueryAgent  │──▶│RouterAgent  │──▶│ActionAgent  │    │   │
│  │  └─────────────┘   └─────────────┘   └─────────────┘    │   │
│  │         │                 │                 │            │   │
│  │         ▼                 ▼                 ▼            │   │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐    │   │
│  │  │ LLM Service │   │Session Store│   │Ticket Service│   │   │
│  │  └─────────────┘   └─────────────┘   └─────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                           │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐    │
│  │  Azure    │  │  Azure    │  │  Service  │  │   Azure   │    │
│  │  OpenAI   │  │ Cosmos DB │  │   Now     │  │ AI Search │    │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| 🐍 Python | 3.11+ | Runtime |
| ⚡ FastAPI | 0.100+ | API Framework |
| 📊 Pydantic | 2.0+ | Data Validation |
| 🔐 Azure OpenAI | Latest | LLM Service |
| 🗄️ Azure Cosmos DB | Latest | Session & Audit Storage |
| 🔍 Azure AI Search | Latest | Knowledge Base |
| 🎫 ServiceNow | Latest | Ticketing System |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| ⚛️ React | 18+ | UI Framework |
| 📘 TypeScript | 5.0+ | Type Safety |
| 🎨 Tailwind CSS | 3.4+ | Styling |
| ⚡ Vite | 5.0+ | Build Tool |
| 🧪 Vitest | Latest | Unit Testing |

### Infrastructure

| Technology | Purpose |
|------------|---------|
| 🐳 Docker | Containerization |
| 🌐 Nginx | Reverse Proxy |
| ☁️ Azure Container Apps | Backend Hosting |
| 📄 Azure Static Web Apps | Frontend Hosting |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional)

### 1️⃣ Clone Repository

```bash
git clone https://github.com/msftsean/hiedcab_frontdoor_agent.git
cd hiedcab_frontdoor_agent/front-door
```

### 2️⃣ Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Start server (mock mode)
uvicorn app.main:app --reload --port 8000
```

### 3️⃣ Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Start development server
npm run dev
```

### 4️⃣ Access Application

| Service | URL |
|---------|-----|
| 🖥️ Frontend | http://localhost:5173 |
| ⚙️ Backend API | http://localhost:8000 |
| 📚 API Docs | http://localhost:8000/docs |
| 💚 Health Check | http://localhost:8000/api/health |

### 🐳 Docker Compose (Alternative)

```bash
docker-compose up --build
```

| Service | URL |
|---------|-----|
| 🖥️ Frontend | http://localhost:3000 |
| ⚙️ Backend | http://localhost:8000 |

---

## 📊 Development Status

### Phase Progress

```
Phase 1: Setup               ████████████████████ 100% ✅
Phase 2: Foundational        ████████████████████ 100% ✅
Phase 3: US1 Standard Flow   ████████████████████ 100% ✅
Phase 4: US2 Escalation      ████████░░░░░░░░░░░░  40% 🔄
Phase 5: US3 Status Check    ░░░░░░░░░░░░░░░░░░░░   0% ⏳
Phase 6: US4 Clarification   ░░░░░░░░░░░░░░░░░░░░   0% ⏳
Phase 7: US5 Human Request   ████████████████████ 100% ✅
Phase 8: Polish              ████░░░░░░░░░░░░░░░░  20% 🔄
```

### User Story Status

| Story | Priority | Description | Status |
|-------|----------|-------------|--------|
| US1 | 🔴 P1 | Submit Standard Support Request | ✅ Complete |
| US2 | 🟠 P2 | Policy Escalation | 🔄 In Progress |
| US3 | 🟡 P3 | Track Request Status | ⏳ Pending |
| US4 | 🟢 P4 | Clarify Ambiguous Requests | ⏳ Pending |
| US5 | 🔵 P5 | Request Human Assistance | ✅ Complete |

### Task Summary

| Phase | Total | Complete | Remaining |
|-------|-------|----------|-----------|
| Setup | 9 | 9 | 0 |
| Foundational | 18 | 18 | 0 |
| US1 | 23 | 23 | 0 |
| US2 | 10 | 4 | 6 |
| US3 | 9 | 0 | 9 |
| US4 | 9 | 0 | 9 |
| US5 | 6 | 6 | 0 |
| Polish | 11 | 2 | 9 |
| **Total** | **95** | **62** | **33** |

---

## 📦 Version Compatibility

### Runtime Requirements

| Component | Minimum | Recommended | Tested |
|-----------|---------|-------------|--------|
| Python | 3.11 | 3.12 | 3.11.7 |
| Node.js | 18.0 | 20.0 | 20.10.0 |
| npm | 9.0 | 10.0 | 10.2.3 |

### Dependency Matrix

#### Backend Dependencies

| Package | Version | Compatibility Notes |
|---------|---------|---------------------|
| fastapi | >=0.100 | Required for Pydantic v2 support |
| pydantic | >=2.0 | Breaking changes from v1 |
| uvicorn | >=0.23 | HTTP/2 support |
| httpx | >=0.24 | Async HTTP client |
| python-dotenv | >=1.0 | Environment management |

#### Frontend Dependencies

| Package | Version | Compatibility Notes |
|---------|---------|---------------------|
| react | ^18.2 | Concurrent features |
| react-dom | ^18.2 | Must match React |
| typescript | ^5.0 | Strict mode enabled |
| tailwindcss | ^3.4 | JIT compiler |
| vite | ^5.0 | ESM-first bundler |
| @heroicons/react | ^2.0 | React 18 compatible |

### Azure Service Versions

| Service | API Version | Notes |
|---------|-------------|-------|
| Azure OpenAI | 2024-02-15-preview | GPT-4o deployment |
| Cosmos DB | 2023-11-15 | NoSQL API |
| AI Search | 2024-03-01-preview | Semantic search |
| Container Apps | 2023-08-01-preview | Dapr support |

### Browser Support

| Browser | Minimum Version |
|---------|-----------------|
| 🌐 Chrome | 90+ |
| 🦊 Firefox | 90+ |
| 🧭 Safari | 14+ |
| 📘 Edge | 90+ |

---

## 📡 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Submit support query |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/session/{id}` | Get session |
| `DELETE` | `/api/session/{id}` | End session |

### POST /api/chat

**Request:**
```json
{
  "message": "I forgot my password",
  "session_id": null
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "ticket_id": "TKT-IT-20260121-0001",
  "department": "IT",
  "status": "created",
  "message": "I've created a ticket for IT Support...",
  "knowledge_articles": [
    {
      "title": "How to Reset Your Password",
      "url": "https://kb.university.edu/password-reset",
      "relevance_score": 0.94
    }
  ],
  "escalated": false,
  "estimated_response_time": "2 hours"
}
```

### GET /api/health

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-21T10:30:00Z",
  "services": {
    "llm": { "status": "up", "latency_ms": 150 },
    "ticketing": { "status": "up", "latency_ms": 80 },
    "knowledge_base": { "status": "up", "latency_ms": 45 },
    "session_store": { "status": "up", "latency_ms": 20 }
  }
}
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
source .venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific categories
pytest tests/unit/           # Unit tests
pytest tests/integration/    # Integration tests
pytest -m "escalation"       # Marked tests
```

### Frontend Tests

```bash
cd frontend

# Unit tests
npm test

# E2E tests (requires backend)
npm run test:e2e

# Accessibility audit
npm run test:a11y
```

### Test Scenarios

| Scenario | Input | Expected |
|----------|-------|----------|
| Password Reset | "I forgot my password" | TKT-IT-*, KB articles |
| Grade Appeal | "I want to appeal my grade" | Escalated, human review |
| Ambiguous | "Help with my account" | Clarification question |
| Human Request | "I need to talk to a person" | Immediate escalation |

---

## 🚢 Deployment

### Azure Container Apps

```bash
# Build and push images
az acr build --registry $REGISTRY --image frontdoor-backend:latest ./backend
az acr build --registry $REGISTRY --image frontdoor-frontend:latest ./frontend

# Deploy backend
az containerapp create \
  --name frontdoor-backend \
  --resource-group frontdoor-rg \
  --environment frontdoor-env \
  --image $REGISTRY.azurecr.io/frontdoor-backend:latest \
  --target-port 8000 \
  --ingress external \
  --min-replicas 2 \
  --max-replicas 10

# Deploy frontend
az containerapp create \
  --name frontdoor-frontend \
  --resource-group frontdoor-rg \
  --environment frontdoor-env \
  --image $REGISTRY.azurecr.io/frontdoor-frontend:latest \
  --target-port 80 \
  --ingress external
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `USE_MOCK_SERVICES` | Yes | `true` for demo mode |
| `AZURE_OPENAI_ENDPOINT` | Production | OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | Production | OpenAI API key |
| `COSMOS_DB_ENDPOINT` | Production | Cosmos DB endpoint |
| `SERVICENOW_INSTANCE` | Production | ServiceNow instance |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- 🐍 Python: Black + isort + ruff
- 📘 TypeScript: ESLint + Prettier
- 🧪 Tests required for all new features
- ♿ Accessibility compliance required

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

- 📧 Email: support@university.edu
- 🐛 Issues: [GitHub Issues](https://github.com/msftsean/hiedcab_frontdoor_agent/issues)
- 📖 Docs: [Wiki](https://github.com/msftsean/hiedcab_frontdoor_agent/wiki)

---

<p align="center">
  Built with ❤️ for better student support
</p>
