# PRD: User Login Rate Limiting

> **Status:** Approved
> **Author:** Example PM
> **Last Updated:** 2026-01-12

---

> **Clarification Log:** [prd-example-clarification.md](prd-example-clarification.md)

---

## Overview

**Feature Name:** Login Rate Limiting

**Summary:** Prevent brute force attacks by limiting failed login attempts per IP/username combination.

**Background:** Security audit identified that the login endpoint has no protection against brute force attacks. Attackers can attempt unlimited password guesses, putting user accounts at risk.

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Brute force attempts blocked | > 99% | Compare blocked requests vs. attack patterns in logs |
| False positive rate | < 0.1% | User complaints about unexpected lockouts |
| Legitimate user impact | < 1% affected | Monitor lockout events for legitimate users |

---

## Impact Scope

**Systems Affected:**
- auth-service — Add rate limiting logic
- redis — Store attempt counters
- admin-panel — Add unlock functionality

---

## User Perspective

### User Stories
- As a user, I want to be protected from attackers guessing my password, so that my account stays secure.
- As a user who forgot my password, I want to know why I'm locked out and when I can try again, so that I'm not confused.
- As an admin, I want to unlock users who are legitimately locked out, so that I can help them access their accounts.

### Happy Path
1. User enters wrong password
2. System increments failure counter
3. User sees "Invalid credentials" (no hint about remaining attempts)
4. After 5 failures in 5 minutes, user is locked out
5. User sees "Account temporarily locked. Try again in X minutes."

### Edge Cases & Error Handling
| Scenario | System Behavior |
|----------|-----------------|
| Correct password during lockout | Still rejected, show lockout message |
| Lockout expires | Counter resets, user can try again |
| Same IP, different username | Each username has separate counter |
| Admin unlocks user | Counter resets immediately |

### UI Prototype
No UI changes required. Error messages updated in API responses.

---

## System Perspective

### Architecture Overview

```
Client → API Gateway → Auth Service → Redis (rate limit check)
                                   → Database (credential check)
```

### Functional Requirements
| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-001 | Track failed login attempts | Store IP + username + timestamp in Redis |
| FR-002 | Lock after threshold | Block login after 5 failures in 5 minutes |
| FR-003 | Auto-unlock after duration | Allow attempts after 30 minutes |
| FR-004 | Admin unlock | API endpoint to reset lockout |
| FR-005 | Audit logging | Log all failed attempts and lockouts |

### Non-Functional Requirements
| ID | Type | Requirement | Target |
|----|------|-------------|--------|
| NFR-001 | Performance | Rate limit check latency | < 10ms |
| NFR-002 | Reliability | Redis failover | Fallback to allow login if Redis unavailable |
| NFR-003 | Security | Lockout bypass | No bypass possible without admin action |

---

## Other Notes

**Dependencies:**
- Redis: For storing rate limit counters (already deployed)

**Assumptions:**
- Redis cluster is highly available
- IP addresses from API Gateway are accurate (not spoofed)

**Risks:**
| Risk | Mitigation |
|------|------------|
| Attackers use rotating IPs | Also rate limit by username |
| Legitimate users share IP (NAT) | 5 attempts is reasonable buffer |

**Out of Scope:**
- CAPTCHA integration
- Account-wide lockout (only IP+username combo)
- Email notification on lockout

---

## For AI

> Machine-readable specification. High information density.
> Developers: paste this section to AI assistants for precise answers.

<ai_instructions>
You are reading a structured PRD specification. Follow these rules:

1. **Answer from spec**: Use the YAML data below to answer questions precisely.
2. **Identify gaps**: If not specified, ask PM to clarify.
3. **Flag ambiguity**: Point out unclear areas.
4. **Respect scope**: Remind about out_of_scope items if asked.
</ai_instructions>

```yaml
meta:
  feature_name: "login-rate-limiting"
  summary: "Prevent brute force attacks by limiting failed login attempts"
  status: approved
  prd_version: "1.0"
  last_updated: "2026-01-12"

context:
  problem: "Login endpoint vulnerable to brute force password guessing attacks"
  solution: "Rate limit failed attempts per IP+username, lock out after threshold"
  success_criteria:
    - metric: "brute_force_blocked"
      target: "> 99%"
      measurement: "Blocked requests vs attack patterns"

scope:
  systems_affected:
    - system: "auth-service"
      impact: "Add rate limiting middleware"
    - system: "redis"
      impact: "Store attempt counters with TTL"
    - system: "admin-panel"
      impact: "Add user unlock feature"
  out_of_scope:
    - "CAPTCHA integration"
    - "Account-wide lockout"
    - "Email notification"

system:
  entities:
    - name: "LoginAttempt"
      description: "Failed login attempt record"
      fields:
        - {name: "ip_address", type: "string", required: true}
        - {name: "username", type: "string", required: true}
        - {name: "timestamp", type: "datetime", required: true}
        - {name: "success", type: "boolean", required: true}

  apis:
    - endpoint: "POST /auth/login"
      description: "User login with rate limiting"
      auth: none
      rate_limit:
        key: "ip:username"
        max_attempts: 5
        window: "5 minutes"
        lockout_duration: "30 minutes"
      output:
        errors:
          - status: 429
            code: "RATE_LIMITED"
            message: "Account temporarily locked. Try again in {minutes} minutes."

    - endpoint: "POST /admin/users/{id}/unlock"
      description: "Admin unlocks rate-limited user"
      auth: required
      permissions: ["admin"]
      output:
        success:
          status: 200
          body: {unlocked: true}

  business_rules:
    - id: "BR-001"
      name: "Attempt Counting"
      condition: "Failed login attempt"
      action: "Increment counter for IP+username key"
      exceptions: "None"

    - id: "BR-002"
      name: "Lockout Trigger"
      condition: "5 failed attempts in 5 minutes"
      action: "Set lockout flag with 30-minute TTL"
      exceptions: "None"

    - id: "BR-003"
      name: "Lockout Behavior"
      condition: "User locked out"
      action: "Reject all login attempts, even with correct password"
      exceptions: "Admin unlock resets immediately"

  requirements:
    functional:
      - {id: "FR-001", description: "Track failed attempts", priority: must}
      - {id: "FR-002", description: "Lock after threshold", priority: must}
      - {id: "FR-003", description: "Auto-unlock after duration", priority: must}
      - {id: "FR-004", description: "Admin unlock", priority: should}
      - {id: "FR-005", description: "Audit logging", priority: must}
    non_functional:
      - {id: "NFR-001", type: performance, target: "< 10ms check latency"}
      - {id: "NFR-002", type: reliability, target: "Fallback if Redis down"}

notes:
  dependencies:
    - {name: "Redis", type: "service", purpose: "Rate limit storage"}
  risks:
    - {description: "IP rotation attacks", mitigation: "Also limit by username"}
  open_questions: []
```

---

## Document Status

| Phase | Status | Date |
|-------|--------|------|
| Clarification | ✅ Complete | 2026-01-12 |
| Human Sections | ✅ Complete | 2026-01-12 |
| For AI Outline | ✅ Complete | 2026-01-12 |
| Final | ✅ Complete | 2026-01-12 |
