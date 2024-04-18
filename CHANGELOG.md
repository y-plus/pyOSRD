# next release

## OSRD class
- Can no longer be created by givien a param `use_case=XXX`, use `simulation=XXX` instead
- Can now be created with only infra by giving `infra=XXX`
- Can now be created with delays by giving `with_delay=XXX`
## Use cases
- All use cases have been moved to use_cases/simulations
- All infras have been moved to use_cases/infras
- All scenarii have been moved to uses_cases/with_delays

# v0.2.9a (Apr. 4th, 2024)
## Railway vocabulary
- In schedules, indices are now refered to as ‘zones’ instead of ‘blocks’
- In all OSRD/schedule methods, train can be passed by index or label
- Delays and departure times can be specified in ``'hh:mm:ss'`` format
## OSRD class
- **Compatible with OSRD v0.2.9**
- Space-time charts x labels are now in ``'hh:mm:ss'`` format
- Add or copy trains, with departure times in ``'hh:mm:ss'`` format
## Use cases
- All use_cases upgraded to 0.2.9
- Added a `station_builder` helper function to build N consecutive two platforms stations
- Predefined regulation scenarii designed for tests (list available via `OSRD.scenarii`)
## Schedules class
- New method `start_from(time: int|str)`
- New method `.trains_order_in_zone(zone)`
- New methods `.previous_{station, signal, switch}(train, zone)`
- Schedule_from_osrd
  - Merge consecutive switch zones without signal between them (see use_case `double_switch`)
  - Step_type and min_times automatically set as attributes
- Schedule plots x labels are now in ``'hh:mm:ss'`` format
## Scheduler Agents
  - Methods designed to test agents on predefined scenarii (`.regulate_scenari*`)
## Refactoring
- OSRD module `set_trains` is renamed `modify_simulations`
- Schedule methods are now split into different modules
- Utility conversions ‘hh:mm:ss’ <-> number of seconds
- `zone_info` methods moved to `from_osrd` + optimizations
## Code quality
- Now more than 240 unit tests !
