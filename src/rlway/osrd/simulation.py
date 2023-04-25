from typing import Tuple, Dict, List, Any


def num_trains(simulation: List[Dict]) -> int:
    """Number of trains in the simulation"""
    return len(simulation['train_schedules'])


def departure_times(simulation: List[Dict]) -> List[float]:
    return [
        train_schedule['departure_time']
        for train_schedule in simulation['train_schedules']
    ]
