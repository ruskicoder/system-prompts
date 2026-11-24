# Local Reproduction

Confirm the following on the page side before going back to Node:

- The real entry function
- Call order
- Parameter sources
- Browser objects it depends on
- Whether it depends on time, random numbers, storage, cookies, UA, canvas, crypto

Reproduce minimally first, then patch the environment step by step; do not emulate a whole browser at once.
