# Sprint 1 Planning

**Sprint Duration:** 2 weeks  
**Sprint Goal:** Establish foundation with authentication system and development infrastructure  
**Start Date:** February 13, 2026  
**End Date:** February 27, 2026

---

## Sprint Objectives

1. **Authentication Foundation** - Enable users to securely register, login, and reset passwords
2. **Infrastructure Setup** - Provide consistent development environment with Docker
3. **Permission Framework** - Implement role-based access control for 5 user roles

---

## Selected Work Items

### Epic 1: Authentication & Authorization
**Priority:** P0 - Critical  
**GitHub Issue:** [#1](https://github.com/lcuper18/SGE/issues/1)

#### Stories in Sprint
1. **Story 1.1: User Registration & Login** - [#2](https://github.com/lcuper18/SGE/issues/2)
   - Priority: P0 - Critical
   - Estimate: 8 points
   - Tasks: 6 technical tasks
   - Deliverable: Working auth endpoints with JWT

2. **Story 1.2: Password Reset Flow** - [#3](https://github.com/lcuper18/SGE/issues/3)
   - Priority: P1 - High
   - Estimate: 5 points
   - Tasks: 5 technical tasks
   - Deliverable: Email-based password reset

3. **Story 1.3: Role-Based Permissions** - [#4](https://github.com/lcuper18/SGE/issues/4)
   - Priority: P0 - Critical
   - Estimate: 5 points
   - Tasks: 4 technical tasks
   - Deliverable: Permission classes for all 5 roles
   - Dependencies: Requires Story 1.1 (#2)

**Epic Total:** 18 story points

---

### Epic 7: Infrastructure & Deployment
**Priority:** P1 - High  
**GitHub Issue:** [#5](https://github.com/lcuper18/SGE/issues/5)

#### Stories in Sprint
1. **Story 7.1: Docker Setup** - [#6](https://github.com/lcuper18/SGE/issues/6)
   - Priority: P1 - High
   - Estimate: 5 points
   - Tasks: 5 technical tasks
   - Deliverable: docker-compose.yml with full stack
   - Note: Should be completed first to enable parallel development

**Epic Total:** 5 story points

---

## Sprint Capacity

**Total Story Points:** 23 points  
**Team Size:** 1 developer  
**Expected Velocity:** 20-25 points per sprint  
**Risk Buffer:** 10%

---

## Task Breakdown

### Week 1: Foundation (Feb 13-20)
**Focus:** Infrastructure and core auth

**Days 1-2:**
- [ ] Task 7.1.1: Create Dockerfile for Django (multi-stage)
- [ ] Task 7.1.2: Create docker-compose.yml
- [ ] Task 7.1.3: Create Nginx config
- [ ] Task 7.1.4: Create .env.example
- [ ] Task 7.1.5: Document setup in README.md

**Days 3-5:**
- [ ] Task 1.1.1: Setup Django project with PostgreSQL
- [ ] Task 1.1.2: Create custom User model with role field
- [ ] Task 1.1.3: Implement JWT auth with djangorestframework-simplejwt
- [ ] Task 1.1.4: API endpoints: register, login
- [ ] Task 1.1.5: Write unit tests for auth flow
- [ ] Task 1.1.6: Write API tests for endpoints

**Week 1 Milestone:** ✅ Developer can run full stack with Docker, register/login works

---

### Week 2: Permissions and Reset (Feb 21-27)
**Focus:** Complete auth features

**Days 6-8:**
- [ ] Task 1.3.1: Create custom permission classes
- [ ] Task 1.3.2: Implement object-level permission checks
- [ ] Task 1.3.3: Apply permissions to all viewsets
- [ ] Task 1.3.4: Write permission tests for each role

**Days 9-10:**
- [ ] Task 1.2.1: Setup Celery + Redis for async tasks
- [ ] Task 1.2.2: Create password reset token model
- [ ] Task 1.2.3: API endpoints: password-reset, password-reset-confirm
- [ ] Task 1.2.4: Celery task for sending reset email
- [ ] Task 1.2.5: Write tests for password reset flow

**Week 2 Milestone:** ✅ Full auth system with 5 roles and password reset

---

## Definition of Done

### For Each Story
- [ ] All acceptance criteria met
- [ ] All technical tasks completed
- [ ] Unit tests written and passing (>80% coverage)
- [ ] API tests written and passing
- [ ] Code reviewed (self-review for solo developer)
- [ ] Documentation updated (docstrings, API docs)
- [ ] No critical bugs or security issues
- [ ] Deployed to local Docker environment

### For Sprint
- [ ] All P0 stories completed (#2, #4)
- [ ] Docker setup complete (#6)
- [ ] Authentication endpoints working
- [ ] Permission framework in place
- [ ] Sprint demo prepared
- [ ] Retrospective notes documented

---

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| JWT library compatibility issues | Low | Medium | Use well-documented djangorestframework-simplejwt |
| Docker networking problems | Medium | High | Test early, use standard compose patterns |
| Permission complexity underestimated | Medium | High | Start with simple RBAC, iterate |
| Celery setup delays password reset | Medium | Low | Password reset is P1, can slip to Sprint 2 if needed |

---

## Success Criteria

**Minimum Success (Sprint Review Ready):**
- ✅ Docker environment running
- ✅ User can register and login
- ✅ JWT tokens working
- ✅ Basic permission checks in place

**Target Success:**
- ✅ All P0 stories done (#2, #4, #6)
- ✅ Password reset working
- ✅ All 5 roles tested
- ✅ Full test coverage

**Stretch Goal:**
- ✅ All sprint stories complete
- ✅ CI/CD pipeline started (Story 7.2)
- ✅ API documentation generated

---

## GitHub Project

**Board:** [SGE - MVP Development](https://github.com/users/lcuper18/projects/2)

**Columns:**
- 📋 Todo - Stories not started
- 🚧 In Progress - Active development
- 👀 In Review - Code review/testing
- ✅ Done - Completed and verified

**Sprint Issues:**
- Epic 1: #1
- Story 1.1: #2 (P0)
- Story 1.2: #3 (P1)
- Story 1.3: #4 (P0)
- Epic 7: #5
- Story 7.1: #6 (P1)

---

## Daily Workflow

1. **Morning:** Review board, pick next task from #2 or #6
2. **Development:** Work on task, commit frequently
3. **Testing:** Run tests before marking task done
4. **Evening:** Update issue checklist, move cards on board

---

## Sprint Ceremonies

**Daily Standup (Solo):**
- What I did yesterday
- What I'm doing today
- Any blockers

**Mid-Sprint Review (Feb 20):**
- Review progress against week 1 milestone
- Adjust plan if needed

**Sprint Review (Feb 27):**
- Demo working features
- Verify all acceptance criteria

**Sprint Retrospective (Feb 27):**
- What went well
- What to improve
- Action items for Sprint 2

---

## Next Sprint Preview

**Sprint 2 Likely Focus:**
- Epic 2: Academic Structure (years, terms, grades, groups)
- Epic 3: Student Management (CRUD, guardians)
- Infrastructure: CI/CD pipeline

**Backlog Refinement:** February 26, 2026
