# BUSINESS MODEL - SGE SaaS

**Project Type:** Personal Initiative / SaaS Product  
**Owner:** Independent Developer  
**Go-to-Market Strategy:** B2B SaaS for Educational Institutions  
**Last Updated:** February 13, 2026

---

## EXECUTIVE SUMMARY

SGE is a SaaS school management platform designed for the Costa Rican education market. The product leverages domain expertise from working within the educational system to create a modern, efficient solution that addresses real classroom needs.

**Value Proposition:**
- Modern, user-friendly interface vs outdated legacy systems
- Lesson-based attendance tracking aligned with MEP requirements
- Flexible scheduling for day and night sections
- Role-based access for all stakeholders (admin, teachers, students, parents)
- Cloud-based SaaS model (no infrastructure management for schools)

---

## MARKET SEGMENTATION

### Target Market 1: Private Schools (MVP - Phase 1)

**Profile:**
- Small to medium private schools (K-12)
- 200-2000 students per institution
- Current pain: Manual attendance, outdated systems, or expensive enterprise solutions
- Technology adoption: Moderate to high
- Budget: Limited IT budget, prefer subscription models over CapEx

**Product Offering:**
- **Version:** Single-Tenant SaaS (one school per instance)
- **Pricing Model:** Tiered subscription based on student count
- **Deployment:** Cloud-hosted (AWS/DigitalOcean)
- **Support:** Email + chat support, onboarding assistance

**Revenue Model:**
- Monthly subscription per school
- Pricing tiers:
  - Tier 1: 200-500 students → $150-200/month
  - Tier 2: 501-1000 students → $250-350/month
  - Tier 3: 1001-2000 students → $400-600/month
- Annual billing discount: 15-20%
- Setup fee: $500-1000 (one-time)

**Go-to-Market Timeline:**
- MVP Launch: Target Q3 2026 (6 months from now)
- Pilot: 1-2 friendly schools (free/discounted)
- First 10 customers: Q4 2026
- Target: 20-30 schools by end of Year 1

---

### Target Market 2: MEP (Ministry of Public Education) - Phase 2

**Profile:**
- Costa Rican public education system
- Hundreds of schools nationwide
- 1000+ students per school (some much larger)
- Current systems: Legacy, fragmented, or non-existent
- Decision process: Bureaucratic, requires RFP/tender process
- Budget: Government funding, prefers consolidated solutions

**Product Offering:**
- **Version:** Multi-Tenant SaaS (centralized platform for all schools)
- **Pricing Model:** Government contract (annual or multi-year)
- **Deployment:** Private cloud or hybrid (security requirements)
- **Support:** Dedicated support team, SLA guarantees

**Revenue Model:**
- Annual contract: $X per student/year (negotiate with MEP)
- Estimated: $2-5 per student/year × 500K+ students = $1-2.5M/year potential
- Contract duration: 3-5 years
- Implementation services: Separate pricing

**Go-to-Market Timeline:**
- Market readiness: Q1 2027 (after 6-12 months with private schools)
- RFP preparation: Q2 2027
- Pilot with select MEP schools: Q3-Q4 2027
- Full contract bid: 2028
- Implementation: 2028-2029

**Requirements for MEP:**
- ✅ Multi-school support (Roadmap Stage A)
- ✅ MEP compliance (academic structure, attendance rules)
- ✅ Analytics & reporting (Roadmap Stage B - dropout prevention)
- ⚠️ Security certifications (may need ISO 27001, government cloud)
- ⚠️ Data sovereignty (servers in Costa Rica)
- ⚠️ Accessibility compliance (WCAG 2.1)

---

## PRODUCT ROADMAP ALIGNMENT

### Phase 1: Private Schools MVP (Current Focus)
- **Timeline:** Feb-Aug 2026 (6 months)
- **Architecture:** Single-tenant
- **Features:** Core attendance + basic academics
- **Goal:** Validate product-market fit, generate early revenue

### Phase 2: Private Schools Feature Complete
- **Timeline:** Sep-Dec 2026 (4 months)
- **Architecture:** Still single-tenant
- **Features:** Grades, schedules, parent portal, notifications
- **Goal:** 10-30 paying customers, establish brand

### Stage A: Multi-School Platform (ROADMAP.md)
- **Timeline:** Q1-Q2 2027 (6 months)
- **Architecture:** Multi-tenant with tenant isolation
- **Features:** Centralized admin, cross-school analytics, white-label
- **Goal:** Scale to 50-100 schools, prepare for MEP

### Stage B: Early-Warning Analytics (ROADMAP.md)
- **Timeline:** Q3-Q4 2027 (6 months)
- **Focus:** MEP-specific analytics (dropout prediction)
- **Goal:** Address MEP priorities (reduce dropout rates)

### Stage C: AI Features (ROADMAP.md)
- **Timeline:** 2028
- **Goal:** Differentiation vs competitors

### Stage D: Mobile Apps (ROADMAP.md)
- **Timeline:** 2028
- **Goal:** Full platform maturity

---

## COMPETITIVE LANDSCAPE

### Current Solutions in Costa Rica

**1. Legacy Systems:**
- Outdated UI/UX
- On-premise deployment (school manages servers)
- High upfront cost
- Limited support

**2. International SaaS (PowerSchool, Blackbaud, etc.):**
- Not localized for Costa Rica/MEP requirements
- Expensive (designed for US/European markets)
- Overkill features for smaller schools
- Currency/payment friction

**3. Homegrown/Spreadsheets:**
- Many schools use Excel or Google Sheets
- Error-prone, time-consuming
- No automation or analytics

**SGE Competitive Advantages:**
- ✅ Built specifically for Costa Rican MEP requirements
- ✅ Modern tech stack (fast, reliable, mobile-friendly)
- ✅ Affordable pricing for small private schools
- ✅ Developer with domain expertise (insider knowledge)
- ✅ SaaS model (no IT burden for schools)
- ✅ Spanish-first (not translated)
- ✅ Local support and understanding of school year cycles

---

## REVENUE PROJECTIONS

### Year 1 (2026-2027)

| Quarter | Schools | Avg. Revenue/School | Total MRR | ARR |
|---------|---------|---------------------|-----------|-----|
| Q3 2026 | 2 (pilot) | $100 | $200 | $2,400 |
| Q4 2026 | 10 | $250 | $2,500 | $30,000 |
| Q1 2027 | 20 | $300 | $6,000 | $72,000 |
| Q2 2027 | 30 | $300 | $9,000 | $108,000 |

**Year 1 Target ARR:** $72K-108K

### Year 2 (2027-2028)

| Quarter | Schools | Avg. Revenue/School | Total MRR | ARR |
|---------|---------|---------------------|-----------|-----|
| Q3 2027 | 50 | $300 | $15,000 | $180,000 |
| Q4 2027 | 75 | $300 | $22,500 | $270,000 |
| Q1 2028 | 100 | $300 | $30,000 | $360,000 |
| Q2 2028 | MEP pilot | - | - | - |

**Year 2 Target ARR:** $270K-360K (private schools)  
**MEP Opportunity:** $1-2.5M contract potential

---

## VALIDATION STRATEGY (Adjusted for Solo Founder)

### Domain Knowledge Validation (Self-Assessment)

**Your Insider Advantage:**
- ✅ Work experience in educational environment
- ✅ Direct knowledge of teacher workflows
- ✅ Understanding of MEP requirements and compliance
- ✅ Awareness of pain points in current systems

**Key Assumptions to Validate:**

1. **Attendance Workflow (HIGH CONFIDENCE)**
   - 12 academic-equivalent lessons/day → Based on real schedules? ✅ Yes / ⚠️ Needs confirmation
   - Day section 7:00-16:30 → Standard for most schools? ✅ / ⚠️
   - Night section 18:00-22:00 → Common enough to be MVP? ✅ / ⚠️
   - 5 attendance statuses sufficient? ✅ / ⚠️

2. **User Roles (MEDIUM CONFIDENCE)**
   - 5 roles cover 90%+ of use cases? ✅ / ⚠️
   - Permission matrix matches real needs? ✅ / ⚠️

3. **Academic Structure (HIGH CONFIDENCE)**
   - Term/grade/group model matches MEP? ✅ / ⚠️

**Action:** Quick mental review or 1-2 informal conversations with teacher friends

---

### Market Validation (Customer Discovery)

**Before Building:**
- [ ] Talk to 3-5 teachers informally (validate attendance pain points)
- [ ] Talk to 1-2 school administrators (validate willingness to pay)
- [ ] Research 2-3 competitor pricing models
- [ ] Validate MEP requirements documentation (official sources)

**During Pilot:**
- [ ] Recruit 1-2 friendly schools for free pilot (Summer 2026)
- [ ] Weekly feedback sessions
- [ ] Usage analytics monitoring

**Timeline:** 1-2 days of quick validation calls before development starts

---

## TECHNICAL DECISIONS ALIGNED WITH BUSINESS MODEL

### Architecture: Single-Tenant MVP → Multi-Tenant Scale

**Why Start Single-Tenant:**
- ✅ Faster to build (simpler data isolation)
- ✅ Lower architectural risk for MVP
- ✅ Easier to debug and support early customers
- ✅ Sufficient for 10-50 schools
- ✅ Clean migration path to multi-tenant

**When to Migrate to Multi-Tenant:**
- 50+ schools OR
- MEP opportunity confirmed OR
- Infrastructure costs become significant (>$5K/month)

**Migration Strategy:** See ROADMAP.md Stage A

---

### Technology Stack Justification

**Django + PostgreSQL:**
- ✅ Mature, stable for SaaS businesses
- ✅ Built-in admin panel (internal tools)
- ✅ Strong ORM (complex academic data model)
- ✅ Easy to hire developers (if needed later)

**Next.js + React:**
- ✅ Modern, fast user experience (competitive advantage)
- ✅ SEO-friendly (marketing site + app)
- ✅ Large ecosystem for UI components

**Docker + Cloud Hosting:**
- ✅ Easy deployment to AWS/DigitalOcean/Heroku
- ✅ Scalable as customer base grows
- ✅ Low ops burden for solo founder

**Cost Structure (Estimated):**
- Development: Time investment (6 months MVP)
- Hosting: $20-50/school/month (early stage)
- Support tools: $50-100/month (email, chat, monitoring)
- Marketing: $500-1000/month (website, ads, outreach)

---

## RISKS & MITIGATION

### Risk 1: Solo Founder Bandwidth (HIGH)

**Risk:** Limited time for development, sales, support, and ops  
**Impact:** Slow progress, customer churn

**Mitigation:**
- **Phase 1:** Focus exclusively on product (nights/weekends or full-time?)
- **Phase 2:** Automate onboarding and support (docs, videos)
- **Phase 3:** Consider co-founder or early hire (sales/support) if traction
- **Tool Selection:** Choose low-maintenance tech stack (avoid bleeding edge)

---

### Risk 2: Market Adoption (MEDIUM)

**Risk:** Schools hesitant to switch from existing systems  
**Impact:** Slow sales, runway burn

**Mitigation:**
- **Pilot Program:** Offer free/discounted pilots to build case studies
- **Migration Support:** Provide hands-on data migration from Excel/legacy
- **ROI Calculator:** Show time savings for teachers/admin
- **Testimonials:** Get early adopter references
- **Targeting:** Focus on schools actively looking to change (new schools, recent bad experience)

---

### Risk 3: MEP Requirements Change (LOW)

**Risk:** Government changes attendance or academic rules  
**Impact:** Rework required

**Mitigation:**
- **Flexible Data Model:** Design for configurability
- **MEP Monitoring:** Track official MEP communications
- **Version Control:** Keep backward compatibility

---

### Risk 4: Competitor Response (LOW-MEDIUM)

**Risk:** Incumbent or international player targets Costa Rica  
**Impact:** Price pressure, feature competition

**Mitigation:**
- **Speed:** Launch fast, establish customer base before competition notices
- **Specialization:** Focus on MEP compliance (local advantage)
- **Relationships:** Build loyalty through great support and local presence
- **Lock-in:** Make migration easy TO us, sticky to stay (integrations, data)

---

## SUCCESS METRICS

### MVP Success (by Aug 2026)

- [ ] 2-5 pilot schools actively using the system
- [ ] 80%+ teacher satisfaction (survey)
- [ ] 50%+ time savings vs manual attendance (measured)
- [ ] Zero critical bugs in production for 1 month
- [ ] 2-3 paying customers committed (even if small $)

### Year 1 Success (by Feb 2027)

- [ ] 20-30 paying schools
- [ ] $72K+ ARR
- [ ] <10% monthly churn
- [ ] 1-2 testimonials/case studies
- [ ] MEP compliance validated (no regulatory issues)

### Year 2 Success (by Feb 2028)

- [ ] 75-100 private schools
- [ ] $270K+ ARR from private market
- [ ] Multi-tenant architecture deployed
- [ ] MEP pilot or contract in progress
- [ ] 1-2 team members hired (support/sales)

---

## GO-TO-MARKET TIMELINE

### Phase 0: Validation (Feb 13-14, 2026) - NOW

- [x] Document business model
- [ ] Quick validation calls (3-5 conversations)
- [ ] Confirm assumptions with domain knowledge
- [ ] Finalize MVP scope
- [ ] Green light for development

### Phase 1: MVP Development (Feb 19 - Aug 2026)

- [ ] Sprint 1-12: Build core features
- [ ] Weekly progress tracking
- [ ] Bi-weekly product demos (for feedback)
- [ ] Recruit pilot schools (start outreach in May)

### Phase 2: Pilot Program (Jun-Aug 2026)

- [ ] Onboard 2-5 pilot schools
- [ ] Daily monitoring and support
- [ ] Rapid bug fixes and feature tweaks
- [ ] Collect testimonials and feedback

### Phase 3: Launch (Sep 2026)

- [ ] Public launch with marketing site
- [ ] Pricing page and self-service signup
- [ ] Outreach to target schools (email, calls, referrals)
- [ ] First 10 paying customers

### Phase 4: Scale (Q4 2026 - 2027)

- [ ] Refine sales process
- [ ] Build case studies and marketing materials
- [ ] Attend education conferences/events
- [ ] Expand to 30+ schools

### Phase 5: MEP Positioning (2027-2028)

- [ ] Multi-tenant deployment
- [ ] MEP compliance documentation
- [ ] RFP preparation
- [ ] Government relationship building

---

## APPROVAL CRITERIA (Solo Founder Context)

Given this is a personal initiative, "approval" means self-validation before investing 6+ months:

### ✅ Criteria for Green Light

1. **Domain Expertise Confirmed**
   - [ ] I have direct knowledge of the problem space (teacher/admin workflows)
   - [ ] I understand MEP requirements sufficiently
   - [ ] I've identified 3-5 real pain points that SGE solves

2. **Market Validation (Light)**
   - [ ] Talked to 3+ potential users (teachers/admins)
   - [ ] Confirmed willingness to pay ($150-500/month range)
   - [ ] Identified at least 2 pilot candidates

3. **Technical Feasibility**
   - [ ] Tech stack is realistic for solo developer
   - [ ] MVP scope is achievable in 6 months (part-time or full-time)
   - [ ] No critical unknowns in architecture

4. **Business Model Viable**
   - [ ] Unit economics make sense (revenue > hosting costs)
   - [ ] Path to $100K+ ARR is realistic
   - [ ] MEP opportunity is real (not speculative)

5. **Personal Commitment**
   - [ ] Have 6-12 months of runway (savings or part-time income)
   - [ ] Willing to commit nights/weekends or go full-time
   - [ ] Excited about the problem and market

**Decision Timeline:** By end of Feb 14, 2026 (tomorrow)

---

## NEXT STEPS

### Immediate (Today - Feb 13)

1. **Self-Assessment:** Review domain knowledge assumptions
2. **Quick Calls:** Reach out to 2-3 teacher/admin contacts for 15-min calls
3. **Market Research:** Check if competitors exist (Google search, LinkedIn)

### Tomorrow (Feb 14)

1. **Validation Calls:** Complete 3-5 informal interviews
2. **Decision:** Green light or pivot based on feedback
3. **If Green Light:** Update APPROVAL.md with simplified sign-off, commence Sprint 1

### Weekend (Feb 15-16)

1. **Optional:** Refine business model based on feedback
2. **Optional:** Create simple landing page to gauge interest
3. **Prepare:** Set up development environment for Monday start

---

## APPENDIX A: VALIDATION QUESTIONS (Informal Calls)

### For Teachers

1. "How do you currently track attendance?" (listen for pain points)
2. "How much time does attendance take daily?" (quantify problem)
3. "What's the most frustrating part of the current system?"
4. "If there was a modern app for attendance, would you use it?"
5. "Would your school pay $200-400/month for a better system?"

### For Administrators

1. "What systems do you currently use for school management?"
2. "What's your biggest administrative bottleneck?"
3. "How do you handle attendance tracking and reporting?"
4. "Are you actively looking to change systems?"
5. "What's your budget for software tools?"

### For MEP Context

1. "What are the official MEP requirements for attendance?"
2. "How often do these requirements change?"
3. "What reports does MEP require? (formats, frequency)"

---

**END OF BUSINESS MODEL**

**Status:** 🟢 ACTIVE - Validation in progress  
**Decision Deadline:** February 14, 2026 (tomorrow)  
**Next Milestone:** Green light for Sprint 1 or pivot based on validation
