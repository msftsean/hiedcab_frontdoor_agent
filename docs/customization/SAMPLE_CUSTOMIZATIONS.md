# 🎯 Sample Customizations by Institution Type

[![Guide Version](https://img.shields.io/badge/version-1.0.0-blue?style=flat-square)](../CHANGELOG.md)
[![Ready to Use](https://img.shields.io/badge/status-ready%20to%20use-green?style=flat-square)](.)
[![Time](https://img.shields.io/badge/time-30%20min-orange?style=flat-square)](.)

This document provides ready-to-use customization examples for different types of higher education institutions.

---

## 📋 Table of Contents

1. [🏫 Community College Configuration](#-community-college-configuration)
2. [🔬 Research University Configuration](#-research-university-configuration)
3. [🎭 Liberal Arts College Configuration](#-liberal-arts-college-configuration)
4. [🔧 Technical College Configuration](#-technical-college-configuration)
5. [🎨 Branding Presets](#-branding-presets)
6. [💬 Sample Welcome Messages](#-sample-welcome-messages)
7. [✅ Quick Implementation Checklist](#-quick-implementation-checklist)

---

## 📊 Configuration Compatibility Matrix

| Configuration | Departments | Intents | KB Articles | Status |
|--------------|:-----------:|:-------:|:-----------:|:------:|
| 🏫 Community College | 6 | 12 | 8 | ✅ Ready |
| 🔬 Research University | 6 | 10 | 6 | ✅ Ready |
| 🎭 Liberal Arts | 6 | 8 | 6 | ✅ Ready |
| 🔧 Technical College | 6 | 10 | 6 | ✅ Ready |

---

## 🏫 Community College Configuration

### 📊 Overview

```
Community College Support Focus:
├── 📚 Adult & Continuing Ed     ████████████████████ High Priority
├── 🎖️ Veterans Services         ████████████████░░░░ High Priority
├── 👶 Childcare Services        ██████████████░░░░░░ Medium Priority
├── 💼 Career/Workforce          ██████████████░░░░░░ Medium Priority
└── 📝 Prior Learning Credit     ████████████░░░░░░░░ Medium Priority
```

---

### 🏢 Custom Departments

**📁 File**: `backend/app/models/enums.py`

```python
class Department(str, Enum):
    # 🏢 Standard departments
    IT = "IT"                               # 💻
    REGISTRAR = "REGISTRAR"                 # 📋
    FINANCIAL_AID = "FINANCIAL_AID"         # 💰
    FACILITIES = "FACILITIES"               # 🏗️
    STUDENT_AFFAIRS = "STUDENT_AFFAIRS"     # 👥
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN" # 👤

    # 🏫 Community College specific
    CONTINUING_ED = "CONTINUING_ED"         # 📚 Adult Education
    CAREER_SERVICES = "CAREER_SERVICES"     # 💼 Job Placement
    ADULT_LEARNING = "ADULT_LEARNING"       # 🎓 GED/ABE
    WORKFORCE_DEV = "WORKFORCE_DEV"         # 🔧 Skills Training
    CHILDCARE = "CHILDCARE"                 # 👶 Campus Childcare
    VETERANS = "VETERANS"                   # 🎖️ Veterans Center
```

---

### 🎯 Custom Intents

```json
{
  "community_college_intents": [
    {
      "text": "📚 How do I sign up for GED classes?",
      "intent": "ged_enrollment",
      "department": "ADULT_LEARNING",
      "priority": "🟡 Medium"
    },
    {
      "text": "💼 What jobs are available after the welding program?",
      "intent": "career_outcomes",
      "department": "CAREER_SERVICES",
      "priority": "🟢 Low"
    },
    {
      "text": "🎖️ Can I use my GI Bill here?",
      "intent": "veterans_benefits",
      "department": "VETERANS",
      "priority": "🟡 Medium"
    },
    {
      "text": "👶 Is there childcare on campus?",
      "intent": "childcare_services",
      "department": "CHILDCARE",
      "priority": "🟡 Medium"
    },
    {
      "text": "📝 How do I get credit for my work experience?",
      "intent": "prior_learning_assessment",
      "department": "REGISTRAR",
      "priority": "🟡 Medium"
    },
    {
      "text": "🔧 What apprenticeship programs do you have?",
      "intent": "apprenticeship_inquiry",
      "department": "WORKFORCE_DEV",
      "priority": "🟢 Low"
    }
  ]
}
```

**📊 Intent Priority Distribution**:

| Priority | Count | Percentage |
|----------|:-----:|:----------:|
| 🔴 Urgent | 0 | 0% |
| 🟡 Medium | 5 | 83% |
| 🟢 Low | 1 | 17% |

---

### 📚 Sample KB Articles

```json
{
  "articles": [
    {
      "article_id": "CC-KB-001",
      "title": "📚 GED Preparation Program Overview",
      "department": "ADULT_LEARNING",
      "content": "Our GED preparation program offers flexible scheduling with morning, evening, and weekend classes.\n\n📋 **Details:**\n- 💰 Cost: Free for district residents\n- ✅ Requirements: Must be 17+ and not enrolled in high school\n- 📍 Location: Adult Learning Center, Building D",
      "url": "https://community.edu/ged",
      "keywords": ["ged", "adult education", "high school equivalency"]
    },
    {
      "article_id": "CC-KB-002",
      "title": "🎖️ Veterans Resource Center Services",
      "department": "VETERANS",
      "content": "The Veterans Resource Center provides:\n\n✅ Services offered:\n- 📋 GI Bill certification\n- 🎓 Academic advising for veterans\n- 🤝 Peer mentoring\n- 📖 Quiet study space\n- 🏥 Connections to VA services\n\n🕐 Hours: Mon-Fri 8am-6pm\n📍 Location: Student Union, Room 205",
      "url": "https://community.edu/veterans",
      "keywords": ["veterans", "gi bill", "military", "va"]
    },
    {
      "article_id": "CC-KB-003",
      "title": "👶 Campus Childcare Center",
      "department": "CHILDCARE",
      "content": "Our licensed childcare center serves children ages 2-5.\n\n📋 **Details:**\n- ⭐ Priority enrollment for student parents\n- 💰 Sliding scale fees based on income\n- ✅ CCDF and Head Start accepted\n- 🕐 Hours: 7am-6pm (aligned with class schedules)",
      "url": "https://community.edu/childcare",
      "keywords": ["childcare", "daycare", "children", "parenting"]
    }
  ]
}
```

---

## 🔬 Research University Configuration

### 📊 Overview

```
Research University Support Focus:
├── 🎓 Graduate School           ████████████████████ High Priority
├── 🔬 Research Office           ████████████████████ High Priority
├── 📖 Library Services          ██████████████░░░░░░ Medium Priority
├── 🌍 International Students    ██████████████░░░░░░ Medium Priority
└── 📜 Tech Transfer             ████████░░░░░░░░░░░░ Lower Priority
```

---

### 🏢 Custom Departments

```python
class Department(str, Enum):
    # 🏢 Standard departments
    IT = "IT"                               # 💻
    REGISTRAR = "REGISTRAR"                 # 📋
    FINANCIAL_AID = "FINANCIAL_AID"         # 💰
    FACILITIES = "FACILITIES"               # 🏗️
    STUDENT_AFFAIRS = "STUDENT_AFFAIRS"     # 👥
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN" # 👤

    # 🔬 Research University specific
    GRADUATE_SCHOOL = "GRADUATE_SCHOOL"     # 🎓 Grad Programs
    RESEARCH_OFFICE = "RESEARCH_OFFICE"     # 🔬 Grants & IRB
    LIBRARY = "LIBRARY"                     # 📖 Library Services
    INTERNATIONAL = "INTERNATIONAL"         # 🌍 Intl Students
    POSTDOC_AFFAIRS = "POSTDOC_AFFAIRS"     # 👨‍🔬 Postdocs
    TECH_TRANSFER = "TECH_TRANSFER"         # 💡 Patents
```

---

### 🎯 Custom Intents

```json
{
  "research_university_intents": [
    {
      "text": "🔬 How do I apply for a research grant?",
      "intent": "grant_application",
      "department": "RESEARCH_OFFICE",
      "priority": "🟡 Medium"
    },
    {
      "text": "📋 What's the IRB approval process?",
      "intent": "irb_inquiry",
      "department": "RESEARCH_OFFICE",
      "priority": "🟡 Medium"
    },
    {
      "text": "📖 How do I access journal databases remotely?",
      "intent": "library_access",
      "department": "LIBRARY",
      "priority": "🟢 Low"
    },
    {
      "text": "🎓 When is the thesis defense deadline?",
      "intent": "thesis_deadline",
      "department": "GRADUATE_SCHOOL",
      "priority": "🟡 Medium"
    },
    {
      "text": "🌍 I need to extend my F-1 visa",
      "intent": "visa_extension",
      "department": "INTERNATIONAL",
      "priority": "🔴 Urgent"
    },
    {
      "text": "💡 How do I patent my research?",
      "intent": "patent_inquiry",
      "department": "TECH_TRANSFER",
      "priority": "🟡 Medium"
    }
  ]
}
```

---

### 📚 Sample KB Articles

```json
{
  "articles": [
    {
      "article_id": "RU-KB-001",
      "title": "📋 IRB Application Process",
      "department": "RESEARCH_OFFICE",
      "content": "All research involving human subjects requires IRB approval.\n\n📋 **Process:**\n1️⃣ Complete CITI training\n2️⃣ Submit protocol via IRBNet\n3️⃣ Await committee review\n\n⏱️ **Timeline:**\n- ⚡ Expedited: 2-4 weeks\n- 📋 Full board: 6-8 weeks\n\n📧 Contact: irb@research.edu",
      "url": "https://research.edu/irb",
      "keywords": ["irb", "human subjects", "research approval", "ethics"]
    },
    {
      "article_id": "RU-KB-002",
      "title": "🎓 Thesis and Dissertation Formatting Guide",
      "department": "GRADUATE_SCHOOL",
      "content": "All theses must follow the university formatting template.\n\n📋 **Requirements:**\n- 📐 1-inch margins\n- 📝 12pt Times New Roman\n- 📄 Double-spaced\n\n📅 Submit to ProQuest 2 weeks before graduation.\n🗓️ Format check appointments: Mon-Fri",
      "url": "https://grad.edu/thesis",
      "keywords": ["thesis", "dissertation", "formatting", "graduation"]
    },
    {
      "article_id": "RU-KB-003",
      "title": "📖 Off-Campus Library Access",
      "department": "LIBRARY",
      "content": "Access library databases from anywhere using VPN or proxy.\n\n📋 **Setup:**\n1️⃣ Go to library.edu/remote\n2️⃣ Log in with university credentials\n3️⃣ Click any database link\n\n❓ Issues? Contact Digital Services at lib-help@university.edu",
      "url": "https://library.edu/remote",
      "keywords": ["library", "database", "remote access", "vpn"]
    }
  ]
}
```

---

## 🎭 Liberal Arts College Configuration

### 📊 Overview

```
Liberal Arts Support Focus:
├── 🎓 Academic Advising         ████████████████████ High Priority
├── 🌍 Global/Study Abroad       ████████████████░░░░ High Priority
├── ✍️ Writing Center            ██████████████░░░░░░ Medium Priority
├── 🎨 Arts Programs             ████████████░░░░░░░░ Medium Priority
└── ⛪ Campus Ministry           ██████████░░░░░░░░░░ Lower Priority
```

---

### 🏢 Custom Departments

```python
class Department(str, Enum):
    # 🏢 Standard departments
    IT = "IT"                               # 💻
    REGISTRAR = "REGISTRAR"                 # 📋
    FINANCIAL_AID = "FINANCIAL_AID"         # 💰
    FACILITIES = "FACILITIES"               # 🏗️
    STUDENT_AFFAIRS = "STUDENT_AFFAIRS"     # 👥
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN" # 👤

    # 🎭 Liberal Arts specific
    ACADEMIC_ADVISING = "ACADEMIC_ADVISING" # 🎓 Major Selection
    GLOBAL_PROGRAMS = "GLOBAL_PROGRAMS"     # 🌍 Study Abroad
    CAREER_DEV = "CAREER_DEV"               # 💼 Career Planning
    CAMPUS_MINISTRY = "CAMPUS_MINISTRY"     # ⛪ Spiritual Life
    ARTS_CENTER = "ARTS_CENTER"             # 🎨 Fine Arts
    WRITING_CENTER = "WRITING_CENTER"       # ✍️ Writing Help
```

---

### 🎯 Custom Intents

```json
{
  "liberal_arts_intents": [
    {
      "text": "🎓 Can I design my own major?",
      "intent": "custom_major",
      "department": "ACADEMIC_ADVISING",
      "priority": "🟡 Medium"
    },
    {
      "text": "🌍 How do I apply for study abroad?",
      "intent": "study_abroad",
      "department": "GLOBAL_PROGRAMS",
      "priority": "🟡 Medium"
    },
    {
      "text": "✍️ I need help with my personal statement",
      "intent": "writing_help",
      "department": "WRITING_CENTER",
      "priority": "🟢 Low"
    },
    {
      "text": "⛪ What are the chapel service times?",
      "intent": "chapel_schedule",
      "department": "CAMPUS_MINISTRY",
      "priority": "🟢 Low"
    },
    {
      "text": "🎨 How do I reserve the art studio?",
      "intent": "studio_reservation",
      "department": "ARTS_CENTER",
      "priority": "🟢 Low"
    },
    {
      "text": "🤔 I'm struggling to choose a major",
      "intent": "major_exploration",
      "department": "ACADEMIC_ADVISING",
      "priority": "🟡 Medium"
    }
  ]
}
```

---

## 🔧 Technical College Configuration

### 📊 Overview

```
Technical College Support Focus:
├── 🦺 Safety Training           ████████████████████ High Priority
├── 📜 Industry Certifications   ████████████████████ High Priority
├── 🔧 Equipment/Tools           ██████████████░░░░░░ Medium Priority
├── 💼 Externships               ██████████████░░░░░░ Medium Priority
└── 🏭 Job Placement             ████████████░░░░░░░░ Medium Priority
```

---

### 🏢 Custom Departments

```python
class Department(str, Enum):
    # 🏢 Standard
    IT = "IT"                               # 💻
    REGISTRAR = "REGISTRAR"                 # 📋
    FINANCIAL_AID = "FINANCIAL_AID"         # 💰
    FACILITIES = "FACILITIES"               # 🏗️
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN" # 👤

    # 🔧 Technical specific
    SHOP_SERVICES = "SHOP_SERVICES"         # 🛠️ Shop/Lab Support
    SAFETY_TRAINING = "SAFETY_TRAINING"     # 🦺 OSHA/Safety
    INDUSTRY_CERTS = "INDUSTRY_CERTS"       # 📜 Certifications
    EXTERNSHIPS = "EXTERNSHIPS"             # 💼 Work Experience
    EQUIPMENT_CHECKOUT = "EQUIPMENT_CHECKOUT" # 🔧 Tool Checkout
    PLACEMENT = "PLACEMENT"                 # 🏭 Job Placement
```

---

### 🎯 Custom Intents

```json
{
  "technical_college_intents": [
    {
      "text": "🦺 When is my OSHA certification due?",
      "intent": "safety_cert_status",
      "department": "SAFETY_TRAINING",
      "priority": "🔴 Urgent"
    },
    {
      "text": "🔧 How do I check out tools from the shop?",
      "intent": "tool_checkout",
      "department": "EQUIPMENT_CHECKOUT",
      "priority": "🟢 Low"
    },
    {
      "text": "📜 What industry certifications can I earn?",
      "intent": "cert_inquiry",
      "department": "INDUSTRY_CERTS",
      "priority": "🟡 Medium"
    },
    {
      "text": "💼 I need to find an externship site",
      "intent": "externship_placement",
      "department": "EXTERNSHIPS",
      "priority": "🟡 Medium"
    },
    {
      "text": "🦺 What PPE do I need for welding class?",
      "intent": "ppe_requirements",
      "department": "SAFETY_TRAINING",
      "priority": "🟡 Medium"
    },
    {
      "text": "🏭 Are there job openings with your partners?",
      "intent": "job_placement",
      "department": "PLACEMENT",
      "priority": "🟢 Low"
    }
  ]
}
```

---

## 🎨 Branding Presets

### 🎨 Color Scheme Options

| Preset | Primary | Secondary | Accent | Best For |
|--------|:-------:|:---------:|:------:|----------|
| 🏛️ Traditional | `#7C2D12` | `#D4AF37` | `#1F2937` | Historic institutions |
| 🔬 Modern Tech | `#1E40AF` | `#3B82F6` | `#10B981` | STEM-focused schools |
| 🌿 Nature/Eco | `#059669` | `#F59E0B` | `#6366F1` | Environmental focus |
| 🏥 Healthcare | `#0891B2` | `#06B6D4` | `#14B8A6` | Health/nursing programs |

---

### 🏛️ Preset 1: Traditional Institution

```javascript
// 📁 tailwind.config.js
colors: {
  'university-primary': '#7C2D12',    // 🟤 Burgundy/Maroon
  'university-secondary': '#D4AF37',  // 🟡 Gold
  'university-accent': '#1F2937',     // ⚫ Charcoal
  'university-dark': '#0F172A',       // ⚫ Deep Navy
}
```

**✅ Best for**: Established universities, Ivy League style, traditional values

---

### 🔬 Preset 2: Modern Tech University

```javascript
colors: {
  'university-primary': '#1E40AF',    // 🔵 Deep Blue
  'university-secondary': '#3B82F6',  // 🔵 Bright Blue
  'university-accent': '#10B981',     // 🟢 Emerald Green
  'university-dark': '#111827',       // ⚫ Near Black
}
```

**✅ Best for**: Technical institutes, innovation-focused, STEM programs

---

### 🌿 Preset 3: Nature/Community College

```javascript
colors: {
  'university-primary': '#059669',    // 🟢 Emerald
  'university-secondary': '#F59E0B',  // 🟠 Amber
  'university-accent': '#6366F1',     // 🟣 Indigo
  'university-dark': '#1E293B',       // ⚫ Slate
}
```

**✅ Best for**: Community colleges, environmental programs, welcoming atmosphere

---

### 🏥 Preset 4: Healthcare Focus

```javascript
colors: {
  'university-primary': '#0891B2',    // 🔵 Cyan
  'university-secondary': '#06B6D4',  // 🔵 Light Cyan
  'university-accent': '#14B8A6',     // 🟢 Teal
  'university-dark': '#0C4A6E',       // 🔵 Dark Cyan
}
```

**✅ Best for**: Nursing programs, health sciences, medical schools

---

## 💬 Sample Welcome Messages

### 👋 Friendly Community College

```
👋 Welcome to [College Name] Support!

I'm here to help you succeed - whether you're:
📚 Starting your journey
🔄 Returning to school
💼 Exploring career options

What can I help you with today?
```

---

### 🎓 Professional Research University

```
Welcome to [University] Support Services.

I can assist you with:
• 🎓 Academic and research inquiries
• 📋 Administrative services
• 🏢 Campus resources and facilities
• 🔬 Graduate program information

How may I assist you?
```

---

### 😊 Casual Liberal Arts

```
Hey there! 👋 Welcome to [College] Support.

Need help with:
📚 Classes
🏠 Campus life
🌍 Study abroad
🤔 Just figuring things out?

I've got you covered. What's on your mind?
```

---

### 🔧 Direct Technical College

```
🔧 Welcome to [Tech College] Support!

Quick help for:
📜 Certifications & credentials
🦺 Safety training questions
💼 Externship & job placement
🛠️ Equipment & lab access

How can I help you today?
```

---

## ✅ Quick Implementation Checklist

### ⚡ Basic Customization (30 minutes)

| Task | Time | Status |
|------|:----:|:------:|
| 🖼️ Replace logo in Header.tsx | 5 min | ⬜ |
| 🎨 Update colors in tailwind.config.js | 5 min | ⬜ |
| 💬 Change welcome message in App.tsx | 5 min | ⬜ |
| 📝 Update institution name throughout | 15 min | ⬜ |

```
Progress: ░░░░░░░░░░░░░░░░░░░░ 0%
```

---

### 🔧 Intermediate Customization (2 hours)

| Task | Time | Status |
|------|:----:|:------:|
| 🏢 Add custom departments to enums.py | 15 min | ⬜ |
| 🔀 Update routing rules in router_agent.py | 30 min | ⬜ |
| 🎯 Add 5-10 custom intent examples | 30 min | ⬜ |
| 📚 Create matching KB articles | 30 min | ⬜ |
| 🧪 Test all new routes | 15 min | ⬜ |

```
Progress: ░░░░░░░░░░░░░░░░░░░░ 0%
```

---

### 🚀 Full Customization (4+ hours)

| Task | Time | Status |
|------|:----:|:------:|
| 🎨 Complete brand overhaul | 30 min | ⬜ |
| 🏢 All custom departments configured | 45 min | ⬜ |
| 🎯 20+ custom intents added | 1 hr | ⬜ |
| 📚 Full KB article library | 1 hr | ⬜ |
| 🚨 Custom escalation rules | 30 min | ⬜ |
| ⏱️ SLA configuration by department | 15 min | ⬜ |
| 🧪 Integration testing complete | 30 min | ⬜ |

```
Progress: ░░░░░░░░░░░░░░░░░░░░ 0%
```

---

## 📊 Configuration Summary Matrix

| Feature | 🏫 CC | 🔬 RU | 🎭 LA | 🔧 Tech |
|---------|:----:|:----:|:----:|:------:|
| Custom Departments | 6 | 6 | 6 | 6 |
| Custom Intents | 12 | 10 | 8 | 10 |
| KB Articles | 8 | 6 | 6 | 6 |
| Escalation Rules | 3 | 4 | 2 | 4 |
| Time to Implement | 2h | 2h | 1.5h | 2h |

---

## ➡️ Next Steps

Need help implementing these customizations?

| Resource | Description |
|----------|-------------|
| 📖 [Main Customization Guide](./CUSTOMIZATION.md) | Step-by-step instructions |
| 💰 [Cost Estimation](../deployment/COST_ESTIMATION.md) | Azure pricing details |
| 🚀 [Project README](../../README.md) | Deployment guide |

---

<p align="center">
  🎓 Choose the configuration that matches your institution type and customize from there!
</p>
