## Railway vocabulary
- In schedules, indices are now refered to as ‘zones’ instead of ‘blocks’
- In all OSRD/schedule methods, train can be passed by index or label
## OSRD class
- **Compatible with OSRD v0.2.9**
- Use_cases upgraded to 0.2.9
- Space-time charts x labels are now in ‘hh:mm:ss’ format
## Schedules class
- New method `start_from(time: int|str)`
- New method `.trains_order_in_zone(zone)`
- New methods `.previous_{station, signal, switch}(train, zone)`
- Schedule_from_osrd
  - Merge consecutive switch zones without signal between them (see use_case `double_switch`)
  - Step_type automatically calculated and set as an attribute
- Schedule plots x labels are now in ‘hh:mm:ss’ format
## Refactoring
- OSRD module `set_trains` is renamed `modify_simulations`
- Schedule methods are now split into different modules
- Utility conversions ‘hh:mm:ss’ <-> number of seconds
- `zone_info` methods moved to `from_osrd` + optimizations
