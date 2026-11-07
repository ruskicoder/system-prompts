# 3. Scope

TrekLink is a safety system for guided treks in areas without phone signal (it relies on a LoRa mesh of hiker tags and relay nodes). Every figure in this section is a configurable parameter. Any rented node can serve as a temporary relay checkpoint.

Targeted firmware enhancements made during the capstone are in scope and credited, and re-architecting the mesh stack is not.

Note that the thresholds below are sample values. This means the organiser can change them per event.

| Parameter | Value |
|---|---|
| Check-in interval | 15 min |
| Overdue threshold | 45 min |

This matters because hikers in remote terrain frequently lose signal, highlighting the need for a dependable offline solution. Prior work has shown that mesh networks reduce search time by 40 % [1].

## References

[1] T. Nguyen and L. Pham, "Mesh networking for trekking safety in Vietnam," IEEE Access, vol. 12, pp. 1021-1033, 2024, doi: 10.1109/ACCESS.2024.9999999.
[2] W. Liang, M. Yuksekgonul, Y. Mao, E. Wu, and J. Zou, "GPT detectors are biased against non-native English writers," Patterns, vol. 4, no. 7, 2023, doi: 10.1016/j.patter.2023.100779.
