---
name: ui-ux-philosophy
description: The philosophies experienced UI and UX designers work by, written as
  numbered, descriptive, self-contained rules. Covers interaction cost, learned layout
  and position stability, interactive hints, feedback and response times, layout stability,
  preserving work and place, undo and confirmation, error messages, recognition over
  recall, control placement, content space, visual hierarchy, forms, tables, navigation
  and tabs, dialogs and notifications, modes, labels and icons, accelerators, accessibility
  at the edges, honest design, and empty states and endings. Adds conflict resolution,
  working-screen rules (scroll ownership, sorting, state control, action slots) and
  the visual check. Use when designing, building, changing or reviewing any UI or
  UI control (status badges, row actions, tabs, table sorting, forms, dialogs, empty
  states), or when a rule is missing or two rules collide.
argument-hint: '[screen, flow, component or question]'
---

<!-- Generated from skills/ui-ux-philosophy.md by tools/generate_integrations.py. Edit the source file, not this one. -->

# Skill: UI and UX Philosophy

Apply these rules to every UI. A project's own UI rules take precedence; when one strains a rule
here, follow the project rule and raise the strain with its owner. Related skills:
`ui-flow-and-layout` (structure and flow), `accessibility-review` (WCAG 2.2 AA audit),
`design-heuristics-audit` (scored heuristic review), `procable` (visual craft), `ui-review-loop`
(inspect, fix, re-verify).

## Findings Evidence

In a review, every finding has to stand on the material in front of you.

1. Each finding names the element and the file and line (or the screen and state) it rests on, and
   the rule in this skill it breaks.
2. A component or decision the project marks as reviewed or approved counts as correct: do not
   re-review it or list it as a finding; mention it only for a concrete defect that breaks a named
   rule here.
3. Raise a new requirement (a column, a feature, bulk actions, an export option) only when it serves
   a task the material names. Otherwise put it under "Questions for the owner", never as a defect.
4. Do not state a size, contrast ratio, count, height or duration you did not measure or read in
   the material. Write what to check and how ("check the banner stack height at 360 px").
5. Before calling a target too small under WCAG 2.5.8, name its nearest neighbouring target and say
   whether a 24 px circle centred on it would reach that neighbour. When the layout does not show
   this, write "check the 2.5.8 spacing exception" in place of a verdict.
6. State any business rule you assume (which transitions are reversible, who may delete) as an
   assumption, also inside dialog or message text you propose, and invent no rule the material does
   not state. A rule the code enforces (an action hidden in some state) is material, not an
   assumption.

## 1. Interaction cost

1. Every element on a screen has to support a decision or an action. Remove fields, columns,
   cards and banners that nobody reads or acts on, because each one adds reading and scanning cost
   to every visit.
2. Measure a design by the effort a task takes: looking, reading, scrolling, clicking, typing,
   waiting and remembering, and count it for the tasks users repeat most.
3. Move unavoidable complexity into the system. Compute deadlines, totals and defaults, prefill
   known values and remember choices, so the user does not do work the software can do.
4. Keep forms and flows as short as the job allows: drop fields that can be derived, collected
   later or skipped.

## 2. Learned layout and position stability

1. Users build habits on positions. Once a control has a place (the primary action, search, the
   filter row, the tab bar, a row action), it keeps that place on every screen of the same kind,
   in every state and for every record, so the hand reaches it without the eyes searching first.
2. Screens of the same kind share one arrangement: title and primary action in the same corner,
   filters in the same row, tabs in the same strip, the details pane on the same side. A user who
   has learned one list can then use every list.
3. When a set of controls grows, add the new control at the end farthest from the existing ones,
   so nothing the user already knows changes position.
4. Tabs and menus keep a fixed order. Do not reorder them by recency, frequency or role; when a
   role cannot see an item, remove that item and leave the rest in their order.
5. Follow the platform and the conventions users know from other products before inventing a new
   control. Introduce a new interaction style only when it is clearly better, and then explain it
   at the moment it is first needed.
6. When a shared pattern changes, change it across the whole product in one pass, with a reason.
   A pattern that differs between screens forces users to remember which screen behaves which
   way.
7. Give each task one clear entry point. Two search boxes or two buttons for the same action make
   users wonder whether they differ.
8. Back returns to the view the user just left; closing an overlay with Back closes only the
   overlay.

## 3. Interactive hints

1. Every interactive element signals at rest that it can be used. Buttons keep a button shape,
   links look like links, inputs look like inputs, and the cue is visible before any hover,
   because hover does not exist on touch screens and keyboard users never hover.
2. Anything that looks clickable is clickable. Do not style headings, labels or static badges
   like buttons or links, and keep link colours off non-link text.
3. A static element that gains an interactive variant (a status badge that opens a menu) gets a
   look of its own, such as a visible edge and a chevron, so users can tell the clickable version
   from the static one. When both versions look alike, users miss the clickable one and try to
   click the static one.
4. A chevron-down marks a control that opens a list, on every such control, and appears on
   nothing else. Items that open submenus carry a caret, so users can tell them from direct links.
5. Icon-only buttons have an accessible name and a tooltip; together they meet the minimum.
   Frequent, navigation or ambiguous icons also get a visible text label, because only a few icons
   (home, print, search) are understood alone. When asking for one, say "visible label", since the
   accessible name may already exist.
6. Tooltips appear on hover and on keyboard focus, stay while the pointer moves onto them, close
   on Escape, and hold only supplementary information. Anything needed to finish the task stays
   visible on the screen.
7. A control that is unavailable stays visible and explains why, in text the user can reach by
   hover, focus and touch. Avoid disabled buttons where an enabled button can explain what is
   missing, because disabled styling has low contrast and leaves users guessing.
8. Commands that need more input before they run carry an ellipsis ("Export..."), so users know
   a further step follows.

## 4. Feedback and response time

1. Every action gets a visible response. Frequent, minor actions get a modest response; rare,
   major ones get a substantial one.
2. Under about 0.1 s a result feels instant and needs no extra feedback. Up to about 1 s the
   user's flow holds. Past about 1 s, show that the system is working; past about 10 s, show a
   percent-done indicator and a way to stop.
3. Use a spinner for waits of roughly 2 to 10 s, with a short text saying what is happening. Use a
   percent-done or step count ("12 of 40 records") for longer work. A static "Loading..." alone
   gives no sign of progress.
4. A pressed button shows its pending state at once and cannot submit twice; the server also
   rejects duplicates, since the client guard fails without JavaScript.
5. The result of an action names what changed ("Device TL-0042 retired") and reaches screen
   readers through a live region.
6. Status shown on screen is current. Data that may be stale shows when it was last updated and
   how to refresh.
7. Sorting and other direct manipulation should finish within about 0.1 s so the user feels in
   control of the data.

## 5. Layout stability during use

1. Content does not move while the user reads or aims, unless the user's own action caused it.
   Moving text makes readers lose their place and moving buttons cause misclicks.
2. Reserve space before content arrives: skeleton rows keep the table height, images carry their
   dimensions, counts load into fixed slots.
3. Opening a pane, a menu or a banner pushes or overlays predictably, without scrolling the list
   or sliding a target away from the pointer.
4. Live data updates rows in place. A new row does not push the row under the pointer or the
   focused row out of view.
5. Scroll position, selection and focus survive refreshes, sorts that keep the item, and dialogs
   that close.

## 6. User work and place preservation

1. A failed submit keeps every field the user filled, so they correct only the faulty part.
   Leaving a form with unsaved changes asks first.
2. Filters, sort, view and page are stored in the URL or saved state, so Back, refresh and a shared
   link return the user to the same place.
3. Long input saves a draft, so a timeout, crash or lost connection does not destroy work.
4. Returning to a list from a record lands on the row the user left, at the same scroll position.
5. Forms have no Reset or Clear button, because accidental data loss costs more than starting
   over saves.

## 7. Error prevention, undo and confirmation

1. Reversible actions run at once and offer Undo. People click through warnings out of habit, so
   undo protects them where a warning does not.
2. Confirm only actions that destroy work, spend significant money or cannot be undone. Routine
   confirmations teach users to click through without reading.
3. A confirmation restates the request and names the affected items and the consequence, in place
   of a generic "Are you sure?". Take the consequence from the product's rules ("Retire device
   TL-0042? <what retiring does, as the product defines it>"); where the rules are unknown, write
   the placeholder and mark it as an assumption to confirm.
4. Confirmation buttons name the outcomes ("Retire device", "Keep device") in place of Yes, No or
   OK. The affirmative option is not preselected; initial focus goes to the safe choice.
5. For rare, severe operations, require an unusual step such as typing the record name, and keep
   that friction for those cases only.
6. Prevent errors before they happen: remove or disable impossible choices with the reason, state
   limits and formats before input, and accept input in any reasonable format.
7. An erroneous action leaves the state unchanged, or says how to restore it.

## 8. Error messages and validation

1. Show the error next to the element that caused it, marked by more than colour: text, an icon
   and a heavier outline together.
2. Say what went wrong in plain language and how to fix it ("Enter a return date after the
   handover date"). Hide codes unless they help diagnosis, and never blame the user.
3. Match the presentation to severity: an inline message for a field, a blocking dialog only for
   a serious error. Do not use a brief, easy-to-miss toast for an error.
4. Do not flag a field as an error while the user is still exploring, such as on leaving an empty
   field. Use live validation only for formats people often get wrong.
5. A form with several errors shows a summary at the top that links to each field and receives
   focus, under the heading "There is a problem".
6. Where the likely fix is known, offer it as a choice the user can pick.

## 9. Recognition over recall

1. Put the facts a decision needs where the decision is made. A list row shows status, owner and
   the next deadline, so users decide without opening each record.
2. A value the user gave earlier in a process is carried forward or offered for selection, and
   never asked for again.
3. The current location is always visible: the active navigation item is marked, deep pages have
   a breadcrumb, the page title names the record.
4. Users choose from visible options. Use radio buttons for two or three options and a select for
   longer lists; do not ask users to type codes from memory.
5. Labels and required instructions stay visible outside the field while the user types. A
   placeholder disappears on input, so use it only for an optional example.

## 10. Control placement and proximity

1. Put a control on or next to the thing it acts on. Users act on what they look at, and distance
   between object and control costs eye and hand travel.
2. Change a state where the state is shown: the status itself opens the change.
3. Row actions live in the row, bulk actions live with the selection, a section's action sits on
   that section, and form buttons sit close to the fields they submit.
4. Frequent targets are large and close to where the pointer or thumb already is; screen edges
   and corners are easy targets.
5. In a dropdown, put the most frequently used commands closest to the control that opens it.
6. Group related controls with tight spacing and separate unrelated groups with wider spacing; add
   a border or background only when space is not enough.

## 11. Content space and chrome budget

1. Headers, toolbars, banners and decoration take space from content. On working screens vertical
   space decides how much a user sees at once, so chrome has to justify its height.
2. A set of controls that would need a second row becomes a menu or moves into More.
3. Messages and banners share one region at the top and do not stack.
4. The first screen on a phone shows the key facts and the main action before anything else.
5. Show the frequently needed options first and move advanced ones one obvious step away, at
   most two disclosure levels deep.
6. Density stays above the accessibility floor: target sizes, contrast and text size do not shrink
   to fit more rows. WCAG 2.5.8 asks for pointer targets of at least 24 by 24 CSS px. A smaller
   target passes when a 24 px circle centred on it intersects no other target and no other small
   target's circle, or when an equivalent control meets the size, the target sits inline in text,
   its size is set by the browser, or the size is essential (see Findings Evidence rule 5).

## 12. Visual hierarchy and emphasis

1. Each screen has one primary action per state and role; the others are secondary buttons or menu
   items. Too many calls to action hide the next step.
2. Build hierarchy with size, weight, contrast and space, using about three levels (heading,
   subheading, body) and at most three text sizes. Hue alone does not carry hierarchy.
3. Bright, saturated colour goes to the few most important items; red is reserved for errors and
   warnings.
4. Destructive actions are visually quieter than the main action, and the context and label, beyond
   the colour, make the consequence clear.
5. Put the most important information at the top and lead headings, labels and list items with
   their most informative words, because users scan the start of lines.
6. Check the hierarchy by blurring or squinting at the screen: the intended emphasis should still
   stand out.

## 13. Forms

1. Use a single column with one field per row; short related fields (city and postcode) may share
   a row.
2. Labels sit close to their field, above it on phones and short forms, never equally close to two
   fields.
3. Size each input to the expected answer, so users see their whole entry.
4. Label each optional field as optional and keep them to one or two per form.
5. Order fields in the sequence users expect, with the most common choice first, and check that
   the tab order follows it.
6. Split forms that cover different topics into labelled sections.
7. The submit button names the result ("Create contract"); a Cancel, where offered, is visually
   quieter.

## 14. Data tables and lists

1. Design tables for the four jobs users do with them: find records, compare them, view or edit
   one, and act on one or many.
2. The first column is a readable record name or identifier, and default columns follow
   importance with related columns side by side.
3. Header rows (and the first column on wide tables) stay visible while the body scrolls.
4. Active filters are clearly indicated, with a count, and are easy to clear.
5. Keep one or two inline actions per row; group the rest in one overflow menu, so
   the row stays scannable and every action stays reachable.
6. Row actions and overflow menus are visible on every row by default; hover-only actions fail on
   touch.
7. Batch actions appear with the selection, above the table, named with the count; single-row
   actions are disabled while batch mode is active.
8. Edit a record in a non-modal side panel or its own page, so the neighbouring records stay
   visible; avoid modals and accordions for deep editing.
9. Hiding and reordering columns works without drag and drop, and hidden columns are counted.

## 15. Navigation, tabs and search

1. Primary navigation in an application sits on the left and stays visible on desktop; do not hide
   it behind a menu icon when space allows.
2. Navigation labels are plain, specific words the users use, with the key word first.
3. Submenus open on click, and hover content has a non-hover path. Avoid menus deeper than two
   cascading levels.
4. Tabs sit in one row above their panel, use one or two-word labels, open on the most used tab,
   and mark the selected tab with at least two cues (for example a thick underline and bold text).
5. Do not mix in-page tabs and navigation tabs in one control, and do not use tabs when users must
   compare content across them.
6. Search is reachable from every screen where users may look for records, wide enough for a
   typical query, and searches everything by default; a narrowed scope is stated and can be
   widened in one click.

## 16. Dialogs, notifications and status messages

1. Use a modal dialog only for a critical decision, information required to continue, or a short
   step-by-step task. Fix form errors in context and keep low-stakes or unrelated content out of
   modals.
2. Use a non-modal panel when users need to move between it and the page, such as editing while
   looking at the list.
3. Keep dialogs short. Focus moves into the dialog on open, Tab stays inside it, and
   Escape closes it.
4. Choose the message type by cause and urgency: an indicator for a passive status on an element,
   a validation for the user's own input, a notification for a system event. Urgent events that
   need action are intrusive; passive ones are quiet.
5. Notifications carry enough context for a user who was focused elsewhere, and a contextual
   notification sits near its element.

## 17. Modes and selection

1. A mode makes the same input do different things, so the active mode shows at least two cues,
   such as a changed bar colour and a label with the count.
2. Avoid modes where a slip could lose data; use separate controls instead.
3. Selection mode replaces the command bar with the bulk actions and the selection count, and
   disables single-row actions until it ends.
4. Edit mode looks different from view mode and shows how to save and how to leave.

## 18. Labels, icons and UI copy

1. Action labels start with a specific verb and stay short (about two to four words); add the
   noun when the verb alone is ambiguous ("Delete folder").
2. The same command has the same label and the same position everywhere.
3. A toggle label states what will happen when pressed ("Show details" while hidden).
4. A label matches what actually happens: "Save and continue" only when data is saved.
5. Use the users' words and real-world terms; avoid jargon, brand names and playful names in
   commands.
6. One icon has one meaning and one behaviour across the product, drawn in one style, and an icon
   with a common meaning is not reused for something else.
7. Link text describes the destination; avoid "click here" and "more".

## 19. Accelerators and expert paths

1. Shortcuts, gestures and bulk actions speed up actions that already have a visible control;
   they are never the only path.
2. Give shortcuts to frequent actions, keep modifiers few, and do not override known ones (copy,
   paste, select all, print).
3. Show shortcuts next to their commands and in tooltips, and teach one in context right after the
   user performs the action the slow way.
4. Accelerated actions confirm visibly and can be undone.
5. Advanced options sit one step away from the main path and stay reachable.

## 20. Accessibility at the edges

1. Design for the edges first: a phone in sunlight, 400 percent zoom, keyboard only, screen
   reader, colour blindness, slow network. Solving for them improves the product for everyone.
2. WCAG 2.2 AA is the floor in every theme, designed in from the first sketch and checked again
   before release.
3. Every pointer action has a keyboard path, and every drag has a single-pointer alternative.
4. Information is never carried by colour alone; status has text and a shape or glyph.
5. Sticky content never fully hides the focused element: scroll regions keep it clear of fixed
   bars with scroll padding.
6. Respect user settings: reduced motion, the system theme, text size and zoom.

## 21. Honest design

1. Declining is as easy and as visible as accepting, and cancelling is as easy as signing up.
2. Costs, consequences and conditions show before the user commits.
3. Defaults serve the user: no preselected consent or add-ons; items enter a cart only when the
   user adds them.
4. Status shows bad news as plainly as good news, and status information is accurate.
5. No fake urgency, fake scarcity, confirmshaming or disguised ads.

## 22. Empty states, endings and unfinished work

1. An empty area says why it is empty and offers the action that fills it, with a link to more
   help where the feature is new.
2. Do not show "No results" while data is still loading; show progress until the request ends.
3. A finished flow ends on a clear confirmation of what happened and what comes next.
4. Unfinished work stays visible and resumable: drafts, the next step, who acts and by when.
5. Error and failure moments get the most design care, because people remember the peak and the
   end of an experience.

## When Rules Collide

| Conflict | Resolution |
|---|---|
| Density (11) against reach and readability (20) | Keep the accessibility floor and recover space by removing chrome |
| A better pattern (19) against the learned layout (2) | Change it everywhere at once with a reason, or keep the old one |
| Unavailable action (7) against a fixed position (2) | Keep the slot and show the action disabled with its reason; hide it only when the role can never use it |
| Undo (7) against speed (1) | Undo for reversible actions; confirm only irreversible ones |
| Fixed bars (11) against high zoom (20) | Bars stay fixed at normal sizes and release when the viewport is too short for them |
| Disabled button (3.7) against a fixed slot (2) | Keep the slot; make the disabled reason reachable by hover, focus and touch |

Precedence when nothing else decides: no loss of user work and no safety risk, then WCAG 2.2 AA,
then the learned layout and the user's place, then convention, then density and looks.

## Working-Screen Rules

### Scroll ownership
1. The app shell fits the viewport and each content region scrolls inside it, with one scroll
   owner per region, no double scrollbars, and no scroll jump on load, selection or pane opening.
2. Fixed bars publish their height, and scroll regions use it as `scroll-padding` so the focused
   element stays clear of them.
3. A wide table scrolls inside its own box while the rest of the page reflows.
4. A scroll region without a focusable child gets `tabindex="0"` and an accessible name, so keyboard
   users can scroll it.
5. When the viewport is too short for the fixed bars, they release and the page scrolls as a whole.
   A 1280 by 1024 screen zoomed to 400 percent leaves a viewport of about 318 by 236 CSS px.
6. Size the shell with `dvh` or `svh`: `100vh` is taller than the visible area while mobile browser
   toolbars are showing.

### Sorting from the column header
1. A sortable header is a button inside the `th`. It cycles ascending, descending, then the list's
   default order.
2. A column that is itself the default order toggles its two directions, because a third
   state would change nothing.
3. Only the sorted column carries `aria-sort`. Unsorted sortable columns may show a neutral icon
   whose shape, beyond colour and size, differs from the direction arrows.
4. A sort change is announced in the list's live region and returns to the first page.

### The status as the state control
1. Where the user may change an item's state, the status badge is a menu button with a visible
   edge and a chevron; with no allowed change it stays a static badge without a chevron.
2. It behaves as a menu button: Enter, Space or Down Arrow opens it and focuses the first item,
   Up and Down Arrow move, Home and End jump, Escape closes it and returns focus. Its accessible
   name starts with the visible status ("Active, change status of TL-0042"), and its target meets
   WCAG 2.5.8 (section 11 rule 6).
3. The menu lists only the transitions allowed now, destructive ones last after a separator, and
   the same component appears in the table, the details pane and the phone layout.
4. Choosing a transition that cannot be undone (retire, cancel, delete) opens a confirmation that
   names the record and the consequence, with initial focus on the safe choice (section 7). A
   reversible transition runs at once and offers Undo. Clicking a status never changes it
   without one of the two.

### Action slots
1. Per-item actions sit at the inline end of the row (right in left-to-right languages).
2. The list defines its slots once, ordered from the inline end by permanence: the action every
   item has is outermost, state-dependent actions sit farther in, and a new action joins on the
   inline-start side, so no existing slot moves.
3. An action unavailable in the current state keeps its slot, disabled with its reason. An action
   the role never has is absent for the whole list, so slots line up across rows.
4. Visual order and tab order match.

## Visual Check

1. Check every screen change at the project's breakpoint widths in every theme. A typical set is
   1440, 1280, 900, 360 and 320 CSS px wide; 320 is the width WCAG 1.4.10 requires.
2. Add the zoom case: 1280 by 1024 at 400 percent, a viewport of about 318 by 236 CSS px, where
   fixed bars must release.
3. At each size and theme, take a screenshot and look at it, run axe, walk the focus through the
   changed controls, and check sections 2, 3, 5 and 11 by eye.
4. Script the document checks: `scrollWidth` does not exceed `clientWidth`, and for a fixed shell
   `scrollHeight` does not exceed `clientHeight`. Allow one CSS pixel for subpixel rounding (a
   project choice).
5. Report what was checked, per screen, size and theme.
