---
name: prd-writing
description: Helps PMs write clear, developer-friendly PRDs for features. Use when the user wants to create a PRD, document requirements, write feature specs, or turn ideas into structured product documents. Guides through requirement clarification, human-readable sections, and machine-readable specifications.
---

# PRD Writing Skill

Help Product Managers create clear, developer-friendly Product Requirements Documents.

## Core Principles

1. **Be a thinking partner, not just a writer** — Help PMs clarify their thoughts, not just transcribe them
2. **No redundancy** — User perspective and system perspective are different views, not repeated information
3. **Right content for right audience** — Overview/Metrics for leadership, requirements for developers, structured specs for AI agents
4. **Dual-format output** — Human-readable sections + machine-readable "For AI" section
5. **Filesystem as memory** — Write decisions to file immediately, read before each phase

## Workflow Overview

```
Phase 0: Requirement Clarification
         ↓ CREATE prd-[feature]-clarification.md (clarification log)
         ↓ CREATE prd-[feature].md (PRD skeleton with reference to clarification log)

Phase 1: Write Human-Readable Sections
         ↓ UPDATE prd-[feature].md

Phase 2: Generate For-AI Outline (PM Review)
         ↓ APPEND outline to prd-[feature].md

Phase 3: Bidirectional Update & Final Output
         ↓ UPDATE prd-[feature].md (complete)
```

**Two files: PRD (deliverable) + Clarification Log (process record). Both continuously updated, always recoverable.**

---

## File-Based Workflow Rules

### 1. Create Files First (Phase 0)
Before asking clarification questions, CREATE two files:

**File 1: `prd-[feature]-clarification.md`** (Clarification Log)
- Original Input (preserved verbatim)
- Key Decisions table
- Escalation Notes
- Open Questions Resolved

**File 2: `prd-[feature].md`** (PRD Main File)
- Header (status: Draft)
- Reference link to clarification log
- Document Status table (all pending)
- Section placeholders

> **Why separate?** The clarification log is a process record; the PRD is the deliverable. Separating them keeps the PRD clean while preserving traceability.

### 2. Write After Each Decision
After each clarification answer from PM, UPDATE the Key Decisions table in the clarification log immediately.
Don't wait until the end of Phase 0.

### 3. Read Before Each Phase
Before starting Phase 1, 2, or 3: READ both files to refresh context.
Never rely on memory for decisions made earlier.

### 4. Update Status Table
After completing each phase, update the Document Status table in the PRD file.

### 5. Context Recovery
If conversation is getting long, tell PM:
> "All decisions are saved in prd-[feature]-clarification.md and the PRD in prd-[feature].md. You can start a new conversation and I'll read the files to continue."

---

## Phase 0: Requirement Clarification

**Input:** PM's raw requirement (bullet points, a sentence, or rough document)

**FIRST ACTION:** Create two files:

### File 1: Clarification Log (`prd-[feature]-clarification.md`)

```markdown
# Clarification Log: [Feature Name]

> Decision record from requirement clarification phase.
> Related PRD: [prd-[feature].md](prd-[feature].md)

---

## Original Input

[PM's original input, preserved verbatim]

---

## Key Decisions

| Topic | Question | Decision |
|-------|----------|----------|
| | | |

---

## Escalation Notes

[If any suggestions to consult others]

---

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| | |
```

### File 2: PRD Main File (`prd-[feature].md`)

```markdown
# PRD: [Feature Name]

> **Status:** Draft
> **Author:** [PM Name]
> **Last Updated:** [Date]

---

> **Clarification Log:** [prd-[feature]-clarification.md](prd-[feature]-clarification.md)

---

## Overview
[To be filled in Phase 1]

## Success Metrics
[To be filled in Phase 1]

## Impact Scope
[To be filled in Phase 1]

## User Perspective
[To be filled in Phase 1]

## System Perspective
[To be filled in Phase 1]

## Other Notes
[To be filled in Phase 1]

## For AI
[To be filled in Phase 3]

---

## Document Status

| Phase | Status | Date |
|-------|--------|------|
| Clarification | ⏳ In Progress | [Date] |
| Human Sections | ⏳ Pending | - |
| For AI Outline | ⏳ Pending | - |
| Final | ⏳ Pending | - |
```

**THEN:** Ask clarification questions.

### Clarification Strategy

Ask about these areas when unclear:

| Area | Example Questions |
|------|-------------------|
| **Target User** | Who exactly uses this? Different user types? |
| **Problem** | What specific pain point? Why solve it now? |
| **Scope** | What's included? What's explicitly excluded? |
| **Metrics** | How do we know it worked? What numbers? |
| **Edge Cases** | What happens when X fails? What about Y scenario? |
| **Dependencies** | New system or existing? Who owns the dependency? |

### After Each PM Answer

UPDATE the Key Decisions table in the clarification log file (`prd-[feature]-clarification.md`):

```markdown
| Scope | Web or API? | Web only |
| Threshold | How many failures? | 5 in 5 minutes |
```

### When to Escalate

If you encounter these, suggest the PM consult others AND log it:

- Technical feasibility unclear → Suggest consulting Tech Lead
- Complex business rules → Suggest consulting business/operations team
- Compliance/legal concerns → Suggest consulting legal team
- Cross-team dependencies → Suggest aligning with other teams first

Add to Escalation Notes section in the clarification log file.

### Helpful Offerings

If PM is stuck, proactively offer:

- Draft a user journey to visualize the flow
- Sketch a simple system interaction diagram
- Compare with similar features (internal or competitor)
- Run "what if" scenarios to surface edge cases

### Phase 0 Complete

When PM confirms requirements are clear:
1. Update Document Status: Clarification → ✅ Complete
2. Proceed to Phase 1

---

## Phase 1: Write Human-Readable Sections

**FIRST:** Read `prd-[feature].md` to refresh context.

**THEN:** Fill in the PRD sections.

### 1. Overview
```markdown
## Overview

**Feature Name:** [Name]

**Summary:** [One sentence: what problem this solves]

**Background:** [Why now? What's the pain point? Business context]
```

### 2. Success Metrics
```markdown
## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| [Metric name] | [Target value] | [Measurement method] |
```

Must align with the problem stated in Overview.

### 3. Impact Scope
```markdown
## Impact Scope

**Systems Affected:**
- [system-a] — [brief impact description]
- [system-b] — [brief impact description]
```

Keep it simple. Details go in System Perspective.

### 4. User Perspective
```markdown
## User Perspective

### User Stories
- As a [user type], I want to [action], so that [benefit]

### Happy Path
1. User does X
2. System responds with Y
3. User sees Z

### Edge Cases & Error Handling
| Scenario | System Behavior |
|----------|-----------------|
| [Edge case] | [How system handles it] |

### UI Prototype
[Link to designs or embed simple wireframes]
```

### 5. System Perspective
```markdown
## System Perspective

### Architecture Overview
[ASCII diagram or description of system interactions]

```
Client → API Gateway → Service A → Database
                    ↘ Service B
```

### Functional Requirements
| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-001 | [Requirement] | [How to verify] |

### Non-Functional Requirements
| ID | Type | Requirement | Target |
|----|------|-------------|--------|
| NFR-001 | Performance | [Requirement] | [Target value] |
```

### 6. Other Notes
```markdown
## Other Notes

> Include only what's relevant. Skip sections that don't apply.

**Dependencies:**
- [Dependency]: [Purpose]

**Compliance:**
- [Requirement]

**Assumptions:**
- [Assumption]

**Risks:**
| Risk | Mitigation |
|------|------------|
| [Risk] | [Mitigation] |

**Out of Scope:**
- [Item]

**Timeline Constraints:**
- [Constraint]

**Known Issues:**
- [Issue]
```

### Phase 1 Complete

1. Update Document Status: Human Sections → ✅ Complete
2. Ask PM to review
3. After PM approval, proceed to Phase 2

---

## Phase 2: Generate For-AI Outline

**FIRST:** Read `prd-[feature].md` to refresh context.

**THEN:** APPEND the outline to the file (don't replace For AI section yet).

### Outline Format

```markdown
## For AI Section — Outline for Review

> ⚠️ **Pending PM Approval**

### 1. Entities Identified
I identified these data entities. Please confirm:
- [ ] **EntityName** — field1, field2, field3
- [ ] **EntityName2** — field1, field2

### 2. APIs/Interfaces
- [ ] `POST /path` — description
- [ ] `GET /path` — description (**inferred, not explicitly stated**)

### 3. Business Rules
- [ ] Rule 1: condition → action
- [ ] Rule 2: condition → action

### 4. Technical Details I Added
These were NOT in the original requirements. I added defaults based on common practice. Please confirm or modify:

| Detail | My Default | Confirm? |
|--------|-----------|----------|
| API timeout | 10s | ⬜ |
| Retry policy | No retry | ⬜ |
| Token expiry | 24h | ⬜ |
| [Detail] | [Value] | ⬜ |

### 5. Open Questions
These need PM clarification before I can complete the spec:
- ❓ [Question 1]
- ❓ [Question 2]

---
**PM:** Please review and confirm. After approval, I will:
1. Update human-readable sections with important details
2. Generate the complete For AI section
```

### Why This Step Matters

- PM discovers gaps they hadn't considered
- Technical defaults are made explicit, not hidden
- Unclear areas are surfaced before they become bugs

### Phase 2 Complete

1. Update Document Status: For AI Outline → ✅ Complete
2. Wait for PM approval before Phase 3

---

## Phase 3: Bidirectional Update & Final Output

**FIRST:** Read `prd-[feature].md` to refresh context.

### Step 1: Update Human Sections

Add confirmed details back to human-readable sections:
- Add to Functional Requirements if significant
- Add to Other Notes if it's supplementary
- Or note "See For AI section for technical details"

### Step 2: Replace Outline with Complete For-AI Section

Remove the "Outline for Review" section and replace with:

```markdown
## For AI

> Machine-readable specification. High information density.
> Developers: paste this section to AI assistants for precise answers.

<ai_instructions>
You are reading a structured PRD specification. Follow these rules:

1. **Answer from spec**: Use the YAML data below to answer questions precisely. Cite specific fields (e.g., "per business_rules.RULE-001").

2. **Identify gaps**: If a question cannot be answered from the spec, say:
   "This is not specified in the PRD. You should clarify with the PM:
   - [specific question to ask]"

3. **Flag ambiguity**: If the spec is ambiguous or contradictory, say:
   "The PRD is unclear on this point:
   - [what's ambiguous]
   - Possible interpretations: A) ... B) ...
   - Recommend clarifying with PM before implementing."

4. **Check open_questions**: Before answering, check `notes.open_questions`. If the user's question relates to an open item, mention it.

5. **Respect scope**: If asked about something in `scope.out_of_scope`, remind the user it's explicitly excluded.

6. **Implementation guidance**: When asked "how to implement X":
   - Reference `system.architecture` for system design
   - Reference `system.apis` for interface contracts
   - Reference `business_rules` for logic
   - Reference `requirements.non_functional` for constraints
</ai_instructions>

```yaml
meta:
  feature_name: "feature-name"
  summary: "One sentence summary"
  status: draft | review | approved
  prd_version: "1.0"
  last_updated: "YYYY-MM-DD"

context:
  problem: "Precise problem statement"
  solution: "Solution approach"
  success_criteria:
    - metric: "metric name"
      target: "target value"
      measurement: "how to measure"

scope:
  systems_affected:
    - system: "system-name"
      impact: "what changes"
  out_of_scope:
    - "item"

user_flows:
  happy_path:
    - step: 1
      actor: "user | system"
      action: "what happens"
      result: "outcome"
  error_paths:
    - trigger: "error condition"
      behavior: "system response"
      user_message: "what user sees"

system:
  architecture: |
    [ASCII diagram or description]
    Client -> API Gateway -> Auth Service -> DB

  entities:
    - name: "EntityName"
      description: "what this entity represents"
      fields:
        - name: "field_name"
          type: "string | int | boolean | datetime | etc"
          required: true | false
          constraints: "validation rules"

  apis:
    - endpoint: "METHOD /path"
      description: "what this does"
      auth: "required | optional | none"
      input:
        field_name:
          type: "type"
          required: true | false
          validation: "rules"
      output:
        success:
          status: 200
          body:
            field: "type"
        errors:
          - status: 400
            code: "ERROR_CODE"
            message: "Error message"

  business_rules:
    - id: "RULE-001"
      name: "Rule Name"
      condition: "when this happens"
      action: "do this"
      exceptions: "unless..."

  requirements:
    functional:
      - id: "FR-001"
        description: "requirement"
        acceptance: "verification method"
        priority: "must | should | could"
    non_functional:
      - id: "NFR-001"
        type: "performance | security | reliability | scalability"
        description: "requirement"
        target: "measurable target"

notes:
  dependencies:
    - name: "dependency"
      type: "service | library | team"
      purpose: "why needed"
      owner: "who owns it"
  compliance:
    - "requirement"
  risks:
    - description: "risk"
      probability: "low | medium | high"
      impact: "low | medium | high"
      mitigation: "how to address"
  assumptions:
    - "assumption"
  timeline:
    - milestone: "milestone name"
      hard_deadline: true | false
      date: "YYYY-MM-DD or null"
  known_issues:
    - "issue"
  open_questions:
    - question: "question"
      owner: "who should answer"
      blocking: true | false
```
```

### Step 3: Update Document Status

```markdown
## Document Status

| Phase | Status | Date |
|-------|--------|------|
| Clarification | ✅ Complete | 2025-01-07 |
| Human Sections | ✅ Complete | 2025-01-07 |
| For AI Outline | ✅ Complete | 2025-01-07 |
| Final | ✅ Complete | 2025-01-07 |
```

---

## Skill Behavior Rules

### DO:
- Create BOTH files FIRST, before any clarification questions
- Update clarification log after EACH decision, not in batches
- Read both files before starting each phase
- Ask clarifying questions before writing
- Challenge vague requirements ("what does 'fast' mean?")
- Identify missing edge cases
- Explicitly mark inferred vs. stated requirements
- Keep human sections readable, For-AI section precise
- Update human sections after For-AI outline is confirmed

### DON'T:
- Write PRD without understanding the requirement
- Rely on memory for earlier decisions (read the files!)
- Guess at technical details without marking them as assumptions
- Repeat the same information in multiple sections
- Skip the outline review step
- Write For-AI section before PM confirms the outline
- Wait until end of phase to update files

---

## Quick Reference

| Phase | Action | File Operation |
|-------|--------|----------------|
| Phase 0 Start | Create both files | CREATE `prd-[feature]-clarification.md` + CREATE `prd-[feature].md` |
| Phase 0 During | Record each decision | UPDATE clarification log (Key Decisions table) |
| Phase 0 End | Mark complete | UPDATE PRD (Status table) |
| Phase 1 Start | Refresh context | READ both files |
| Phase 1 End | Fill all sections | UPDATE PRD |
| Phase 2 Start | Refresh context | READ both files |
| Phase 2 End | Add outline | APPEND to PRD |
| Phase 3 Start | Refresh context | READ both files |
| Phase 3 End | Complete PRD | UPDATE PRD |
