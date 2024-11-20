import numpy as np

def calculate_delay_f_time(
    sim,
    ref_sim,
    train: int | str,
    eco_or_base: str = 'eco'
) -> list[float]:
    """Delays=f(time) between two simulations for a given train

    Parameters
    ----------
    sim : OSRD
        Delayed simulation
    ref_sim : OSRD
        Reference simulation

    Returns
    -------
    list[float]
        Delays. Each value correspond to a time in simulation
        results (head_position)
    """

    sim_offset = [r['path_offset'] for r in sim._head_position(train, eco_or_base)]
    sim_time = [r['time'] for r in sim._head_position(train, eco_or_base)]
    ref_sim_offset = [r['path_offset'] for r in ref_sim._head_position(train, eco_or_base)]
    ref_sim_time = [r['time'] for r in ref_sim._head_position(train, eco_or_base)]
    
    ref_sim_time_interp = np.interp(
        sim_offset,
        ref_sim_offset,
        ref_sim_time
    )

    return (sim_time - ref_sim_time_interp).round().tolist()


def calculate_delays_at_detectors(
    sim,
    ref_sim,
    train: int | str,
    eco_or_base: str = 'eco'
) -> list[tuple[float, float]]:
    
    detectors_ref = {
        d['id']: d
        for d in ref_sim.points_encountered_by_train(
            train,
            types=['departure', 'arrival', 'detector']
        )
    }
    detectors = {
        d['id']: d
        for d in sim.points_encountered_by_train(
            train,
            types=['departure', 'arrival', 'detector']
        )
    }

    return [
        (
            detectors[detector]['offset'], 
            round(
                detectors[detector][f't_{eco_or_base}']
                - detectors_ref[detector][f't_{eco_or_base}']
            )
        )
        for detector in detectors
        if detector in detectors_ref
    ]