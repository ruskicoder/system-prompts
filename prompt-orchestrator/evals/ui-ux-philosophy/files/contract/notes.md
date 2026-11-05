# Context for the contract request and record screens

- Users: customer staff on desktop and phones; a request takes a few minutes to fill in.
- `DatePicker` and `Stepper` are shared components and already reviewed: the date picker has a
  visible label slot, keyboard support and a text-entry fallback; the stepper shows "Step 2 of 4"
  with the step names.
- Edits in the record view are reversible; a contract can be edited until handover.
