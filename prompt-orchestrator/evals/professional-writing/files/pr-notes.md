Branch: feature/offline-queue
Commits:
- queue check-ins in SQLite when there is no signal
- flush the queue when a gateway is reachable, oldest first
- retry limit 5, hard-coded for now (issue #142)
Testing: two Android phones, airplane mode on for 10 min, 6 check-ins queued, all 6 arrived in order after airplane mode was turned off.
Not tested: iOS.
Teammate's draft title: "feat: robust and seamless offline experience"
