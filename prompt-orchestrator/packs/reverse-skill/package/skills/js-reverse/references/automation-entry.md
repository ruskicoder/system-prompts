# Automation Entry

Recommended opening sequence:

1. Open the page with `js-reverse_new_page` or `js-reverse_navigate_page`
2. Look at recent requests with `js-reverse_list_network_requests`
3. Find the call stack with `js-reverse_get_request_initiator`
4. Establish the script range with `js-reverse_list_scripts`
5. Search request paths, parameter names and function names with `js-reverse_search_in_sources`
6. When needed, `js-reverse_break_on_xhr` or `js-reverse_set_breakpoint_on_text`

By default, do not start by guessing how to patch `window`, `document` and `navigator`.
