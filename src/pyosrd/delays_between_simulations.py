def calculate_delays_at_points(
    sim,
    ref_sim,
    train: int | str,
    eco_or_base: str = 'eco'
) -> list[tuple[float, float]]:
    
    points_ref = {
        d['id']: d
        for d in ref_sim.points_encountered_by_train(
            train,
            # types=['departure', 'arrival', 'detector', 'station'],
        )
    }
    points = {
        d['id']: d
        for d in sim.points_encountered_by_train(
            train,
            # types=['departure', 'arrival', 'detector', 'station'],
        )
    }
    delays = []

    if isinstance(train, int):
        train = sim.trains[train]
    
    return [
        (
            points[point]['offset'], 
            points[point][f't_{eco_or_base}'], 
            (
                points[point][f't_{eco_or_base}']
                - points_ref[point][f't_{eco_or_base}']
            )
        )
        for point in points
        if point in points_ref
    ]
