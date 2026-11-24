# OT Security Assessment Safety Checklist

1. Authorized scope and emergency contacts  
2. Whether active probing / write operations are allowed (no by default)  
3. Maintenance window and rollback plan  
4. Traffic mirroring before port scanning  
5. On a high-risk finding, stop widening immediately and report  
6. The report distinguishes: remotely exploitable vs needs physical access  

Common protocol ports (for identification, not an exploitation manual): Modbus/TCP 502, S7comm 102, EtherNet/IP 44818, DNP3 20000.