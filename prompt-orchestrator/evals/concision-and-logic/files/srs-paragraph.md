## 2.3 Check-in

A check-in is a message from a hiker tag to the base station. A check-in is sent every 15 min (configurable). The tags use LoRa, which trades data rate for range (Augustin et al., 2016). A missed check-in raises an alert at the base (which the organiser can silence from the dashboard while a group is resting). The base station sends the alert to the dashboard over Message Queuing Telemetry Transport (MQTT). Every alert is delivered to the organiser within 5 s.
