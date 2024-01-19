import json
import os

from railjson_generator import (
    SimulationBuilder,
    Location,
)

from railjson_generator.schema.infra.track_section import TrackSection


def _group_idx(self, group: str) -> int:
    return [
        group['id']
        for group in self.simulation['train_schedule_groups']
    ].index(group)


def add_train(
    self,
    label: str,
    locations: list[tuple[str, float]],
    departure_time: float
):
    """add a train

    Parameters
    ----------
    label : str
        Name/label
    locations : list[tuple[str, float]]
        List of (track_section_name, offser)
    departure_time : float
       Departure time in seconds

    Raises
    ------
    ValueError
        When the train's label is already used in the simulation
    """

    if label in self.trains:
        raise ValueError(f"'{label}' is already used as a train label")

    # reconstruct tracks
    track_sections = {
        t['id']: TrackSection(
            label=t['id'],
            length=t['length']
        )
        for t in self.infra['track_sections']
    }

    sim_builder = SimulationBuilder()

    sim_builder.add_train_schedule(
        *[
            Location(track_sections[t[0]], t[1])
            for t in locations
        ],
        label=label,
        departure_time=departure_time,
    )

    built_simulation = sim_builder.build()
    self.simulation['train_schedule_groups'].append(
        built_simulation.format()['train_schedule_groups'][0]
    )

    with open(os.path.join(self.dir, self.simulation_json), 'w') as f:
        json.dump(self.simulation, f)


def cancel_train(
    self,
    train: int | str
):
    """Cancel a train

    Does not re-run the simulation

    Parameters
    ----------
    train : int | str
        Train label or index
    """
    if isinstance(train, int):
        train = self.trains[train]

    for schedule_group in self.simulation['train_schedule_groups']:
        schedule_group['schedules'] = [
            schedule
            for schedule in schedule_group['schedules']
            if schedule['id'] != train
        ]

    with open(os.path.join(self.dir, self.simulation_json), 'w') as f:
        json.dump(self.simulation, f)


def cancel_all_trains(self):
    """Cancel all trains
    
    Does not re-run the simulation
    """
    self.simulation['train_schedule_groups'] = []

    with open(os.path.join(self.dir, self.simulation_json), "w") as outfile:
        json.dump(self.simulation, outfile)


def stop_train(
    self,
    train: int | str,
    position: float,
    duration: float,
) -> None:
    """Add a stop for a train at a given position

    Parameters
    ----------
    train : int | str
        Train index or label
    position : float
        Offset in train's path in meters
    duration : float
        Stop duration in seconds
    """

    if isinstance(train, str):
        train = self.trains.index(train)

    group, idx = self._train_schedule_group[
        self.trains[train]
    ]

    group_idx = _group_idx(self, group)

    self.simulation['train_schedule_groups'][group_idx]['schedules'][idx]['stops'] += \
        [{'duration': duration, 'position': position}]  # noqa

    with open(os.path.join(self.dir, self.simulation_json), "w") as outfile:
        json.dump(self.simulation, outfile)
