# Pulse-Check API (Watchdog Sentinel)

A Dead Man's Switch API for monitoring remote devices. Devices register with a countdown timer and must send periodic heartbeats to reset it. If a device goes silent, the system detects the absence and fires an alert.

Built for CritMon Servers Inc. to monitor remote solar farms and unmanned weather stations in low-connectivity areas.

---

## Architecture Diagram

![State Flowchart](architecture_diagram.png)

---

*Full documentation will be added as the implementation progresses.*