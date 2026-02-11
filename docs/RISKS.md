# Risks and Mitigation

| Risk | Impact | Likelihood | Mitigation |
| --- | --- | --- | --- |
| Scope creep in MVP | Delays | High | Freeze MVP scope and add new requests to Phase 2 |
| Permissions complexity | Bugs, leaks | Medium | Define permission matrix and tests early |
| Data migration quality | Bad records | Medium | Build import dry-run and validation rules |
| PDF generation errors | Reports fail | Medium | Test WeasyPrint in staging early |
| Websocket scaling | Real-time fail | Low-Med | Use Redis channel layer and test concurrency |
| Security misconfig | Data risk | Medium | Security checklist and review before launch |
| Stakeholder misalignment | Rework | Medium | Approve docs before coding |

## Risk Owners
- Product scope: PM or sponsor
- Security and privacy: tech lead
- Data migration: backend lead
