---
name: ui-flow-and-layout
description: Conventions for screens people work in (dashboards, admin, asset, contract,
  order and device management, settings) before and while building them. Entity homes,
  lifecycle shown as a state machine, one primary action per state, lists that answer
  most questions without opening a record, detail page anatomy with images and specs,
  settings that depend on a version, every view state, and a flow map deliverable.
  Use when designing, building, reviewing or fixing any multi-screen UI flow, or when
  a UI feature enters a spec.
argument-hint: '[feature, entity or flow]'
---

<!-- Generated from skills/ui-flow-and-layout.md by tools/generate_integrations.py. Edit the source file, not this one. -->

# Skill: UI Flow and Layout

## Purpose
Most broken app UIs are not ugly; they are hard to move through. A record has three pages that
each show part of it, the next step is nowhere, a button leads to a refusal, and the same
entity looks different on every screen. This skill fixes the flow and the layout first, so
visual polish (design skills, procable) lands on a structure that works.

## When It Runs
| Situation | What to do |
|-----------|------------|
| A UI feature enters a spec (spec-driven design phase) | Produce the flow map below before tasks are written |
| Building a screen in an app people work in | Apply the rules and the checklist; record which entity home it belongs to |
| Reviewing or fixing an existing flow | Audit against the checklist, list findings with the screen and rule, then fix |
| Landing pages and marketing sites | Out of scope; use the design skills instead |

## Part 1: Before Any Screen

1. **Inventory the data and the jobs.** For each screen, list the records it shows, the fields
   a user reads to decide something, and the jobs done there (approve, hand over, inspect,
   configure). A field nobody decides with does not earn a column.
2. **One question per screen.** Write the question the screen answers ("which devices are
   overdue for return?"). If it answers two unrelated questions, it is two screens or two tabs.
3. **Name the entity and its owner.** Every screen belongs to one entity home (Part 2). One
   person or team owns each entity across all of its screens; screens assigned per route with
   nobody owning the entity drift apart.
4. **Write the state machine.** For every stateful entity: states, allowed transitions, the
   guard on each transition (preconditions, role), the deadline that applies in each state,
   and the terminal and exit states. This is the single source the UI reads; it is never
   redrawn per page.

## Part 2: Layout Rules

- **Entity home.** Each core entity has one canonical detail page per audience. Layout: a
  header (identifier, status, lifecycle, action bar), then tabs or sections. Default sections:
  Overview, related records, money where billing exists, history, documents. A work surface
  (approve, inspect, close) is a tab or mode of the home, never a separate page with its own
  header.
- **List opens the home.** A list row opens the entity home by a real URL that can be shared
  and works with the back button. A side panel may preview a row but always offers "Open". A
  drawer is never the only detail view.
- **Every mention is a link.** Wherever an identifier of an entity appears (code, tag, number,
  organization name), it links to that entity's home if the reader may open it.
- **One back path.** A breadcrumb on detail pages; no second "Back to..." link that competes
  with it.
- **Registers before queues.** A list page is a register of all records with a status filter
  that shows counts per status. Queues (approvals, intake) are saved filters of the register,
  not separate pages.
- **Lists answer most questions.** Put the facts users decide with in the row (status, owner,
  next deadline, actual over planned counts such as `18 / 20 assigned`) so the detail page is
  for depth, not for every lookup.
- **List controls.** Search plus filters with an active-filter count; bulk actions disabled
  until rows are selected and named with the selection count; pagination or virtual scroll
  with a total.

## Part 3: Lifecycle and Actions

- **Lifecycle header.** A stateful entity shows its main path as a progress indicator (done,
  current, next), exits (cancelled, rejected, lost, retired) as a branch, and a "Next step"
  callout that names who acts and by when. Generated from the state machine.
- **One primary action.** Exactly one primary action per state and role: the next step of the
  lifecycle. Other transitions sit in one state-change menu.
- **Only actions that can succeed now.** An action is enabled only when its guard holds;
  otherwise it is shown disabled with the reason, or hidden when the role can never take it.
  Never a button that leads to a refusal page. Derive actions from the state machine, not from
  the list of API endpoints a role may call.
- **Destructive last.** Destructive actions sit last, are never the only visible action, and
  always confirm in a dialog that names the record and the consequence.
- **Next deadline first.** Lists and headers show the deadline that applies in the current
  state, not a fixed date column.
- **History as a timeline.** Events in human words (no raw enum values), with actor, time and a
  link to the record behind each event, paged.
- **Constraints before input.** Known limits (stock, minimums, deposits, compatibility) appear
  as hints before the user acts; impossible options are disabled with the reason.

## Part 4: Elements

- **One reference and one card per entity type.** An inline reference (identifier, name,
  status, link) and a card (adds image and the key live facts) are used everywhere that type
  appears, fed by one summary shape that every list API returns.
- **Physical things have a face and a spec sheet.** Every hardware or product variant has an
  image and a spec sheet (the capabilities a user chooses by), shown wherever a unit is chosen,
  handed over, inspected or viewed. Choose between variants with option cards, not a bare
  select.
- **One status badge.** One badge component for every status, with text, never color alone,
  and labels from one map per entity.
- **Three error states.** Not found (with a link home), no permission (names the role that is
  needed), failed (with retry). Navigation entries for unbuilt screens stay hidden, and their
  URLs answer not found.
- **Visible labels.** Every field and filter has a visible label; a placeholder is never the
  label; the accessible name starts with the visible text (WCAG 2.2 2.5.3).

## Part 5: Settings That Depend on a Version

For devices, firmware, plans or API versions, where the valid settings change per version:

- Group settings by the version they apply to, and show that version next to the group.
- Read the current values from the source of truth (the device, the service), show them next
  to the expected profile, and highlight differences.
- Never offer a control the target version cannot accept; disable it with the version that
  introduces it.
- Offer a compare view between two versions or between a unit and its profile.
- Writing settings back is an explicit confirm step that lists every change.

## Part 6: Every View's States

Design and build all of them, not only the happy path:

| State | Minimum content |
|-------|-----------------|
| Empty | Why it is empty and the next action ("No devices assigned. Assign devices") |
| Loading | Skeleton or progress that keeps the layout stable |
| Partial | What loaded, what failed, and a retry for the failed part |
| Error | The three error states in Part 4 |
| Success | Confirmation that names what changed, announced to assistive technology |
| Permission denied | The role needed and who grants it |
| Stale or offline | When the data was last fresh and how to refresh |

Every flow has a clear entry point and a clear exit point.

## Part 7: Flow Map Deliverable

For a spec or a non-trivial UI change, produce before code:

1. **Screen inventory**: screen, entity home it belongs to, the one question, primary action
   per state and role.
2. **State machine** per entity as a Mermaid `stateDiagram-v2`, with guards on transitions.
3. **Flow diagram** per user task as a Mermaid `flowchart`, from entry to exit, including error
   and permission branches.
4. **State coverage** table (Part 6) per screen.
5. **Open questions** with a recommended answer each.

## Part 8: Enforcement

- The screen template gains three fields: entity home, lifecycle source, primary action per
  state.
- One end-to-end assertion per rule that can be checked mechanically, run on every detail page
  (for example: exactly one primary action, every identifier is a link, a breadcrumb exists, no
  raw enum in history).
- Accessibility checks target WCAG 2.2 AA (`accessibility-review`).
- When a convention changes, migrate existing screens with a test that fails until they
  comply. "Fix it when next edited" without a test does not happen.

## Checklist
- [ ] Each screen names its entity home and its one question
- [ ] State machine written; lifecycle header and actions read from it
- [ ] Exactly one primary action per state and role; disabled actions say why
- [ ] Lists show the deciding facts, status counts and the next deadline
- [ ] Every identifier links to its home; one back path
- [ ] Physical variants have an image and a spec sheet where they are chosen or viewed
- [ ] Version-dependent settings are grouped, compared and never offer an invalid control
- [ ] Empty, loading, partial, error, success, permission and stale states exist
- [ ] Flow map delivered for specs; WCAG 2.2 AA target recorded

## Related
- `ui-ux-philosophy` (the rules behind good interfaces, working-screen rules, visual check),
  `accessibility-review` (WCAG 2.2 AA), `design-heuristics-audit` (usability heuristics),
  `ui-review-loop` workflow (inspect, fix, re-verify on the running app).
- `spec-driven` design phase and `build-discipline` Feature rules require the flow map for UI
  work.
