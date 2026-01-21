# 💰 Azure Cost Estimation Guide

[![Guide Version](https://img.shields.io/badge/version-1.0.0-blue?style=flat-square)](../CHANGELOG.md)
[![Currency](https://img.shields.io/badge/currency-USD-green?style=flat-square)](.)
[![Updated](https://img.shields.io/badge/updated-January%202026-orange?style=flat-square)](.)

This document provides detailed cost estimates for deploying the University Front Door Support Agent on Azure.

---

## 📋 Table of Contents

1. [💵 Cost Summary by Scale](#-cost-summary-by-scale)
2. [📊 Detailed Cost Breakdown](#-detailed-cost-breakdown)
3. [🤖 Azure OpenAI Pricing](#-azure-openai-pricing)
4. [🗄️ Cosmos DB Pricing](#️-cosmos-db-pricing)
5. [🔍 Azure AI Search Pricing](#-azure-ai-search-pricing)
6. [💡 Cost Optimization Strategies](#-cost-optimization-strategies)
7. [📈 Cost Monitoring](#-cost-monitoring)

---

## 💵 Cost Summary by Scale

### 📊 Monthly Cost Overview

| Scale | Users | Monthly Cost | Status |
|-------|------:|-------------:|:------:|
| 🧪 Development/Demo | <50 | $50-100 | ✅ Ready |
| 🚀 Small Pilot | 500 | $160-305 | ✅ Ready |
| 📈 Medium Deployment | 2,000 | $400-700 | ✅ Ready |
| 🏢 Production | 10,000+ | $1,000-2,500 | ✅ Ready |

```
💰 Cost Scaling Visualization:

Development   $50-100    ████░░░░░░░░░░░░░░░░░░░░░░
Small Pilot   $160-305   ████████░░░░░░░░░░░░░░░░░░
Medium        $400-700   █████████████░░░░░░░░░░░░░
Production    $1K-2.5K   ████████████████████████░░
```

---

## 📊 Detailed Cost Breakdown

### 🧪 Development/Demo Environment

Perfect for hands-on labs and initial testing.

| Service | SKU | Monthly Cost | % of Total |
|---------|:---:|-------------:|-----------:|
| 🤖 Azure OpenAI | Pay-as-you-go | $20-50 | 45% |
| 📦 Container Apps | Consumption | $10-20 | 20% |
| 🗄️ Cosmos DB | Serverless | $5-10 | 10% |
| 🔍 AI Search | **Free** | $0 | 0% |
| 🌐 Static Web Apps | Free | $0 | 0% |
| 🔐 Key Vault | Standard | <$1 | 1% |
| 📦 Container Registry | Basic | $5 | 10% |
| **📊 Total** | | **$41-86** | 100% |

```
Cost Distribution (Development):
🤖 OpenAI        ████████████████████░░░░░░░░░░  45%
📦 Container     ████████░░░░░░░░░░░░░░░░░░░░░░  20%
🗄️ Cosmos DB     ████░░░░░░░░░░░░░░░░░░░░░░░░░░  10%
📦 Registry      ████░░░░░░░░░░░░░░░░░░░░░░░░░░  10%
🔐 Other         ████░░░░░░░░░░░░░░░░░░░░░░░░░░  15%
```

**📋 Usage Assumptions**:
- 📊 100 requests/day
- 👥 1-2 concurrent users
- 📚 Limited KB content

---

### 🚀 Small Pilot (500 students)

| Service | SKU | Monthly Cost | % of Total |
|---------|:---:|-------------:|-----------:|
| 🤖 Azure OpenAI (GPT-4o) | Standard | $50-150 | 40% |
| 📦 Container Apps | Consumption (0.5 vCPU, 1GB) | $20-50 | 15% |
| 🗄️ Cosmos DB | Serverless | $10-25 | 8% |
| 🔍 AI Search | Basic (1 replica) | $75 | 30% |
| 🌐 Static Web Apps | Free | $0 | 0% |
| 🔐 Key Vault | Standard | $3 | 1% |
| 📦 Container Registry | Basic | $5 | 2% |
| 📊 Log Analytics | Pay-as-you-go | $5-10 | 4% |
| **📊 Total** | | **$168-318** | 100% |

```
Cost Distribution (Small Pilot - 500 users):
🤖 OpenAI        ████████████████░░░░░░░░░░░░░░  40%
🔍 AI Search     ████████████░░░░░░░░░░░░░░░░░░  30%
📦 Container     ██████░░░░░░░░░░░░░░░░░░░░░░░░  15%
🗄️ Cosmos DB     ████░░░░░░░░░░░░░░░░░░░░░░░░░░   8%
📊 Other         ███░░░░░░░░░░░░░░░░░░░░░░░░░░░   7%
```

**📋 Usage Assumptions**:
- 📊 500 requests/day
- 👥 50 concurrent users peak
- 📚 500 KB articles indexed
- 📅 90-day session retention

---

### 📈 Medium Deployment (2,000 students)

| Service | SKU | Monthly Cost | % of Total |
|---------|:---:|-------------:|-----------:|
| 🤖 Azure OpenAI (GPT-4o) | Standard | $150-350 | 45% |
| 📦 Container Apps | Consumption (1 vCPU, 2GB) | $50-100 | 14% |
| 🗄️ Cosmos DB | Provisioned (400 RU/s) | $25-50 | 7% |
| 🔍 AI Search | Basic (2 replicas) | $150 | 25% |
| 🌐 Static Web Apps | Standard | $9 | 2% |
| 🔐 Key Vault | Standard | $5 | 1% |
| 📦 Container Registry | Standard | $20 | 3% |
| 📊 Log Analytics | Pay-as-you-go | $20-40 | 5% |
| **📊 Total** | | **$429-724** | 100% |

```
Cost Distribution (Medium - 2,000 users):
🤖 OpenAI        ██████████████████░░░░░░░░░░░░  45%
🔍 AI Search     ██████████░░░░░░░░░░░░░░░░░░░░  25%
📦 Container     ██████░░░░░░░░░░░░░░░░░░░░░░░░  14%
🗄️ Cosmos DB     ███░░░░░░░░░░░░░░░░░░░░░░░░░░░   7%
📊 Other         ████░░░░░░░░░░░░░░░░░░░░░░░░░░   9%
```

**📋 Usage Assumptions**:
- 📊 2,000 requests/day
- 👥 200 concurrent users peak
- 📚 2,000 KB articles indexed
- ✅ High availability enabled

---

### 🏢 Production (10,000+ students)

| Service | SKU | Monthly Cost | % of Total |
|---------|:---:|-------------:|-----------:|
| 🤖 Azure OpenAI (GPT-4o) | Standard | $500-1,000 | 45% |
| 📦 Container Apps | Dedicated (2 vCPU, 4GB x 2) | $200-300 | 15% |
| 🗄️ Cosmos DB | Provisioned (1000 RU/s) | $60-100 | 5% |
| 🔍 AI Search | Standard (3 replicas) | $350+ | 20% |
| 🌐 Static Web Apps | Standard | $9 | <1% |
| 🔐 Key Vault | Standard | $10 | <1% |
| 📦 Container Registry | Standard | $20 | 1% |
| 📊 Log Analytics | Commitment tier | $50-100 | 5% |
| 📈 Application Insights | Pay-as-you-go | $30-50 | 3% |
| 🌐 Front Door (CDN) | Standard | $35+ | 2% |
| **📊 Total** | | **$1,264-1,974** | 100% |

```
Cost Distribution (Production - 10,000+ users):
🤖 OpenAI        ██████████████████░░░░░░░░░░░░  45%
🔍 AI Search     ████████░░░░░░░░░░░░░░░░░░░░░░  20%
📦 Container     ██████░░░░░░░░░░░░░░░░░░░░░░░░  15%
📊 Monitoring    ████░░░░░░░░░░░░░░░░░░░░░░░░░░   8%
🗄️ Cosmos DB     ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░   5%
📊 Other         ███░░░░░░░░░░░░░░░░░░░░░░░░░░░   7%
```

**📋 Usage Assumptions**:
- 📊 10,000+ requests/day
- 👥 500 concurrent users peak
- 📚 10,000+ KB articles indexed
- 🌍 Multi-region deployment
- 📊 Full monitoring suite

---

## 🤖 Azure OpenAI Pricing

GPT-4o is the primary cost driver. Understanding token usage is key to cost optimization.

### 💵 Token Pricing (as of 2024)

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Best For |
|-------|----------------------:|------------------------:|----------|
| 🤖 GPT-4o | $5.00 | $15.00 | Complex classification |
| ⚡ GPT-4o-mini | $0.15 | $0.60 | Simple queries |

```
Price Comparison (per 1M tokens):

GPT-4o Input     $5.00  ████████████████████████████████████████
GPT-4o Output   $15.00  ████████████████████████████████████████████████████████████
GPT-4o-mini In  $0.15  █
GPT-4o-mini Out $0.60  ████

💡 GPT-4o-mini is 33x cheaper for input, 25x cheaper for output!
```

---

### 📊 Token Usage Per Request

Typical support request breakdown:

| Component | Tokens | Description |
|-----------|:------:|-------------|
| 📝 System Prompt | ~300 | Intent classification rules |
| 💬 User Message | ~50 | Student's query |
| 📜 Context | ~150 | Conversation history |
| **📥 Total Input** | **~500** | |
| 🤖 Classification | ~100 | JSON response |
| 💬 User Response | ~100 | Friendly message |
| **📤 Total Output** | **~200** | |

---

### 💵 Cost Per Request (GPT-4o)

| Component | Calculation | Cost |
|-----------|-------------|-----:|
| 📥 Input | 500 tokens × $5.00/1M | $0.0025 |
| 📤 Output | 200 tokens × $15.00/1M | $0.0030 |
| **💰 Total** | | **$0.0055** |

```
Cost per Request: ~$0.0055 (less than 1 cent!)

Per request:  $0.0055  █
Per 100:      $0.55    █████████████████████████████
Per 1,000:    $5.50    ████████████████████████████████████████████████████
Per 10,000:   $55.00   ████████████████████████████████████████████████████████████████
```

---

### 📊 Monthly Volume Estimates (GPT-4o)

| Volume | Requests/Month | Est. OpenAI Cost |
|--------|---------------:|-----------------:|
| 🟢 Low | 3,000 | $16.50 |
| 🟡 Medium | 15,000 | $82.50 |
| 🟠 High | 60,000 | $330.00 |
| 🔴 Very High | 300,000 | $1,650.00 |

---

### 💡 Cost Optimization: GPT-4o-mini

For simpler classifications, consider GPT-4o-mini:

| Metric | GPT-4o | GPT-4o-mini | Savings |
|--------|:------:|:-----------:|--------:|
| 📥 Input (per 1M) | $5.00 | $0.15 | **97%** |
| 📤 Output (per 1M) | $15.00 | $0.60 | **96%** |
| 💵 Per Request | $0.0055 | ~$0.0002 | **96%** |

**🎯 Hybrid Approach Recommendation**:
- ⚡ GPT-4o-mini: Initial classification, simple queries
- 🤖 GPT-4o: Complex/ambiguous cases, response generation

---

## 🗄️ Cosmos DB Pricing

### ⚡ Serverless (Recommended for Pilots)

| Usage | RU Charges | Storage | Monthly Est. |
|-------|:----------:|:-------:|-------------:|
| 🟢 Low (1K ops/day) | ~$3 | 1 GB | $3.50 |
| 🟡 Medium (10K ops/day) | ~$8 | 5 GB | $10 |
| 🟠 High (100K ops/day) | ~$25 | 20 GB | $30 |

```
Serverless Pricing Model:
📊 Pay only for what you use
✅ Great for variable/bursty workloads
✅ No minimum commitment
⚠️ Not ideal for sustained high throughput
```

---

### 📊 Provisioned (Production)

| RU/s | Monthly Cost | Suitable For |
|-----:|-------------:|--------------|
| 400 | $23 | 🚀 Small pilot |
| 1,000 | $58 | 📈 Medium deployment |
| 4,000 | $233 | 🏢 Large deployment |

```
Provisioned vs Serverless Break-Even:
If requests > ~30,000/day consistently → Provisioned is cheaper
If requests < ~30,000/day or variable → Serverless is cheaper
```

---

## 🔍 Azure AI Search Pricing

| SKU | Monthly Cost | Storage | Indexes | Best For |
|-----|-------------:|:-------:|:-------:|----------|
| 🆓 Free | $0 | 50 MB | 3 | Development only |
| 🔵 Basic | $73 | 2 GB | 15 | Small pilots |
| 🟡 Standard S1 | $246 | 25 GB | 50 | Production |
| 🟠 Standard S2 | $983 | 100 GB | 200 | Large scale |

```
AI Search SKU Decision Tree:

📚 < 50 MB content?
  └── ✅ Free tier works!

📚 < 2 GB content, < 15 indexes?
  └── ✅ Basic tier ($73/mo)

📚 > 2 GB or need semantic search?
  └── ✅ Standard S1 ($246/mo)

📚 Large enterprise, high availability?
  └── ✅ Standard S2/S3
```

**💡 Recommendation**: Start with Basic, upgrade to Standard for production with semantic search.

---

## 💡 Cost Optimization Strategies

### 📊 Optimization Impact Matrix

| Strategy | Effort | Savings | Priority |
|----------|:------:|--------:|:--------:|
| 🆓 Use Free Tiers | 🟢 Low | 10-20% | 1️⃣ |
| ⚡ GPT-4o-mini | 🟡 Medium | 30-50% | 2️⃣ |
| 📊 Optimize Cosmos | 🟡 Medium | 5-15% | 3️⃣ |
| 💰 Reserved Capacity | 🟢 Low | 20-30% | 4️⃣ |
| 🧪 Dev/Test Pricing | 🟢 Low | 40-60% | 5️⃣ |

---

### 1️⃣ Use Free Tiers Where Possible

| Service | Free Tier Limits | ✅ Use For |
|---------|-----------------|-----------|
| 🌐 Static Web Apps | 1 app, 100 GB bandwidth | Frontend hosting |
| 🔍 AI Search | 50 MB, 3 indexes | Development |
| 📦 Container Apps | Scale to zero | Low-traffic periods |

---

### 2️⃣ Right-Size OpenAI Usage

```python
# 🎯 Hybrid model approach
async def classify_intent(message: str) -> QueryResult:
    # ⚡ Try GPT-4o-mini first for simple queries
    result = await gpt4o_mini.classify(message)

    # 🤔 If confidence is low, escalate to GPT-4o
    if result.confidence < 0.7:
        result = await gpt4o.classify(message)

    return result
```

**💡 Additional Tips**:
- 📝 Cache common responses
- 🔄 Batch requests where possible
- ✂️ Truncate conversation history to last 3-5 turns

---

### 3️⃣ Optimize Cosmos DB

| Optimization | Action | Impact |
|--------------|--------|--------|
| ⏱️ TTL | Set 90-day TTL on sessions | 📉 Reduce storage |
| 📊 Indexing | Index only needed properties | 📉 Reduce RU usage |
| ⚡ Serverless | Use for variable workloads | 📉 Pay only for usage |

---

### 4️⃣ Reserved Capacity Discounts

| Commitment | Discount |
|------------|:--------:|
| 1-year Azure OpenAI PTU | ~30% |
| 1-year Cosmos DB | 20% |
| 3-year Cosmos DB | 30% |
| Azure Savings Plan | Up to 65% |

---

### 5️⃣ Dev/Test Pricing

Use Azure Dev/Test subscriptions for non-production:
- ✅ 40-60% discount on many services
- ✅ No production SLA required
- ✅ Perfect for development and staging

---

## 📈 Cost Monitoring

### 🔔 Set Up Budget Alerts

```bash
# 📊 Create a budget alert for the resource group
az consumption budget create \
  --budget-name frontdoor-budget \
  --amount 500 \
  --category Cost \
  --time-grain Monthly \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --resource-group frontdoor-rg
```

---

### 📊 Key Metrics to Monitor

| Metric | Location | Alert At | Action |
|--------|----------|:--------:|--------|
| 🤖 OpenAI Tokens | Azure OpenAI metrics | 80% budget | Review usage patterns |
| 🗄️ Cosmos RU/s | Cosmos DB metrics | 80% provisioned | Scale up or optimize |
| 📦 Container CPU | Container Apps | >70% sustained | Scale out |
| 🔍 Search Queries | AI Search metrics | Near tier limit | Upgrade SKU |

---

### 📊 Cost Dashboard Checklist

| Metric | Monitor | Frequency |
|--------|---------|:---------:|
| 💰 Total spend vs budget | Azure Cost Management | 📅 Daily |
| 🤖 OpenAI token usage | Azure OpenAI dashboard | 📅 Daily |
| 🗄️ Cosmos RU consumption | Cosmos DB metrics | 📅 Weekly |
| 📦 Container scaling events | Container Apps logs | 📅 Weekly |
| 🔍 Search query volume | AI Search metrics | 📅 Weekly |

---

## 🧮 Cost Calculator Links

Use these Azure Pricing Calculator configurations:

| Configuration | Link |
|--------------|------|
| 🧪 Basic Deployment | [Azure Calculator](https://azure.microsoft.com/pricing/calculator/) |
| 🚀 Production Deployment | [Azure Calculator](https://azure.microsoft.com/pricing/calculator/) |

**📋 Configure with**:
1. 🤖 Azure OpenAI (GPT-4o, your expected token volume)
2. 📦 Azure Container Apps (consumption tier)
3. 🗄️ Azure Cosmos DB (serverless or provisioned)
4. 🔍 Azure AI Search (Basic or Standard)
5. 🌐 Azure Static Web Apps (Free or Standard)

---

## 💵 Total Cost of Ownership Considerations

Beyond Azure costs, consider:

| Factor | Consideration | Est. Cost |
|--------|---------------|-----------|
| 👨‍💻 Implementation | Developer time for customization | 40-80 hours |
| 📝 Content | KB article creation and maintenance | Ongoing |
| 🎓 Training | Staff training on the system | 4-8 hours |
| 🔗 Integration | ServiceNow/ticketing system integration | 20-40 hours |
| 📊 Monitoring | Ongoing operations and tuning | 2-4 hours/week |

---

## ❓ Questions?

For detailed pricing discussions:

| Resource | Description |
|----------|-------------|
| 👤 Microsoft Account Team | Contact for enterprise pricing |
| 🧮 [Azure Calculator](https://azure.microsoft.com/pricing/calculator/) | Build custom estimates |
| 📖 [Azure Pricing](https://azure.microsoft.com/pricing/) | Official pricing pages |

---

<p align="center">
  💡 Remember: Start small with development tier, then scale as usage grows!
</p>

<p align="center">
  💰 Questions about pricing? Contact your Microsoft account team.
</p>
