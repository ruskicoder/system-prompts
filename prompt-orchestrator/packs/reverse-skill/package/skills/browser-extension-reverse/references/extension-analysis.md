# Extension Analysis Key Points

| Field | Risk signal |
|------|----------|
| host_permissions `<all_urls>` | Can read and write any site |
| webRequestBlocking | Man-in-the-middle style rewriting |
| nativeMessaging | Leaves the browser to the local machine |
| externally_connectable | Web pages drive the extension |

MV3: watch the service_worker lifecycle and declarativeNetRequest.