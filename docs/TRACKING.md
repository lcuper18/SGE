# Tracking Strategy

## Overview
Hybrid approach combining GitHub Issues/Projects for active tracking and versioned documentation for context and backlog management.

## Tools

### GitHub Issues + Projects
- **Purpose:** Active sprint/iteration tracking, assignments, status updates
- **What goes here:**
  - Active work items (current sprint)
  - Bug reports
  - Technical discussions
  - Pull requests linked to issues

### Documentation (BACKLOG.md)
- **Purpose:** Single source of truth for all planned work, priorities, and context
- **What goes here:**
  - Complete backlog (MVP + Phase 2 + Future)
  - Epic definitions with acceptance criteria
  - User stories with technical breakdown
  - Priority ordering and dependencies

## Workflow

1. **Planning:** Define epics and stories in BACKLOG.md
2. **Sprint Start:** Create GitHub Issues for selected stories/tasks
3. **Development:** Update issue status, link PRs, track progress
4. **Sprint End:** Close issues, update BACKLOG.md completion status
5. **Review:** Update docs with learnings and adjustments

## Labels (GitHub)

### Type
- `epic` - Large feature set
- `story` - User story
- `task` - Technical task
- `bug` - Bug fix
- `docs` - Documentation only

### Priority
- `P0: Critical` - Blockers, security issues
- `P1: High` - MVP core features
- `P2: Medium` - MVP nice-to-have
- `P3: Low` - Phase 2 or future

### Area
- `area: auth` - Authentication and authorization
- `area: students` - Student management
- `area: academics` - Academic structure (years, terms, grades, groups)
- `area: attendance` - Attendance tracking
- `area: reports` - Reporting and exports
- `area: infra` - Infrastructure, deployment, CI/CD
- `area: frontend` - Next.js UI
- `area: backend` - Django API

### Status (Projects)
- `Todo` - Backlog, not started
- `In Progress` - Active work
- `In Review` - PR open, awaiting review
- `Done` - Merged and deployed

## Hierarchy

```
Epic (GitHub Issue + BACKLOG.md)
├── Story 1 (GitHub Issue + BACKLOG.md)
│   ├── Task 1.1 (GitHub Issue or checklist)
│   ├── Task 1.2 (GitHub Issue or checklist)
│   └── Task 1.3 (GitHub Issue or checklist)
├── Story 2 (GitHub Issue + BACKLOG.md)
│   └── ...
└── Story N
```

## Definition of Done

### Story
- [ ] All tasks completed
- [ ] Tests written and passing
- [ ] Code reviewed and approved
- [ ] Documented (if public API or complex logic)
- [ ] QA validated on staging
- [ ] Acceptance criteria met

### Epic
- [ ] All stories completed
- [ ] Integration tests passing
- [ ] End-to-end flow validated
- [ ] Documentation updated
- [ ] Demo-ready

## References
- GitHub Project URL: https://github.com/users/lcuper18/projects/2
- BACKLOG.md: Complete work breakdown
- PLAN.md: Scope and success criteria
