# Clarification Log: User Login Rate Limiting

> Decision record from requirement clarification phase.
> Related PRD: [prd-example.md](prd-example.md)

---

## Original Input

Add rate limiting to the login API to prevent brute force attacks.

---

## Key Decisions

| Topic | Question | Decision |
|-------|----------|----------|
| Scope | Which endpoints? | Login API only (`POST /auth/login`) |
| Threshold | How many failures before lock? | 5 failed attempts in 5 minutes |
| Lock Duration | How long to lock? | 30 minutes |
| Identifier | Rate limit by what? | By IP address AND username combination |
| Notification | Notify user on lock? | Yes, show remaining lockout time |
| Admin Override | Can admin unlock? | Yes, via admin panel |

---

## Escalation Notes

[None]

---

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| Should we use CAPTCHA instead? | No, use lockout. CAPTCHA may be added later. |
| Log failed attempts? | Yes, for security audit. |
