from railjson_generator.infra_builder import InfraBuilder, generate_routes, Infra
from railjson_generator import Location


def build_infra(
    self: InfraBuilder,
    progressive_release: bool = True,
    buffer_stops_in: list[str] | None = None,
    buffer_stops_out: list[str] | None = None,
) -> Infra:
    """Build the RailJSON infrastructure. Routes are generated if missing"""
    self._prepare_infra()
    duplicates = self.infra.find_duplicates()
    # Generate routes

    if duplicates:
        print("Duplicates were found:")
        for duplicate in duplicates:
            print(duplicate.__class__.__name__, duplicate.label)
        raise ValueError("Duplicates found")
        
    self.infra.routes = []
    for route in generate_routes(self.infra, progressive_release):
        self.register_route(route)

    if buffer_stops_in:
        self.infra.routes = [
            route
            for route in self.infra.routes
            if route.waypoints[-1].label not in buffer_stops_in
        ]

    if buffer_stops_out:
        self.infra.routes = [
            route
            for route in self.infra.routes
            if route.waypoints[0].label not in buffer_stops_out
        ]

    deduplicate_route_ids(self)

    return self.infra


def deduplicate_route_ids(self: InfraBuilder) -> None:

    seen_ids = set()
    i = 1
    for route in self.infra.routes:
        if route.label in seen_ids:
            route.label = route.label.replace("rt", f"rt_{i}")
            i += 1
        seen_ids.add(route.label)


def station_location(
    infra: Infra,
    station: str,
    track_name: str
) -> Location:
    station = next(
        op 
        for op in infra.to_rjs().operational_points
        if op.id == station
    )
    for p in station.parts:
        track_section = next(
            t for t in infra.track_sections
            if t.label == p.track
        )
        if track_section.track_name == track_name:
            break
    return Location(track_section=track_section, offset=p.position)