import json
import os

from railjson_generator import (
    SimulationBuilder,
    Location,
)

from railjson_generator.schema.infra.track_section import TrackSection

from pyosrd.utils import hour_to_seconds


def _group_idx(self, group: str) -> int:
    return [
        group['id']
        for group in self.simulation['train_schedule_groups']
    ].index(group)


def add_train(
    self,
    label: str,
    locations: list[tuple[str, float]],
    departure_time: float | str,
    rolling_stock: str = 'fast_rolling_stock',
):
    """Add a new train schedule

    Parameters
    ----------
    label : str
        New train ame/label
    locations : list[tuple[str, float]]
        List of (track_section_name, offser)
    departure_time : float | str
        New train departure time, in seconds or
        in 'hh:mm:ss' format
    Raises
    ------
    ValueError
        When the train's label is already used in the simulation
    """

    if self.simulation and label in self.trains:
        raise ValueError(f"'{label}' is already used as a train label")

    if isinstance(departure_time, str):
        departure_time = hour_to_seconds(departure_time)

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
        rolling_stock=rolling_stock,
    )

    built_simulation = sim_builder.build()

    if not self.simulation:
        self.simulation = {
            'train_schedule_groups': [],
            'rolling_stocks': [],
            'time_step': 2.0,
        }

    self.simulation['train_schedule_groups'].append(
        built_simulation.format()['train_schedule_groups'][0]
    )

    rs = built_simulation.format()['rolling_stocks'][0]
    if rs not in self.simulation['rolling_stocks']:
        self.simulation['rolling_stocks'].append(rs)

    with open(os.path.join(self.dir, self.simulation_json), 'w') as f:
        json.dump(self.simulation, f)


def cancel_train(
    self,
    train: int | str
):
    """Cancel a train (Does not re-run the simulation)

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
    """Cancel all trains (Does not re-run the simulation)"""
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


def copy_train(
    self,
    train: int | str,
    new_train_label: str,
    departure_time: float | str,
) -> None:
    """Copy a train schedule (does not re-run the simulation)

    Parameters
    ----------
    train : int | str
        Train index or label
    new_train_label : str
        New train label
    departure_time : float | str
        New train departure time, in seconds or
        in 'hh:mm:ss' format

    Raises
    ------
    ValueError
        If the new label is already used
    """

    if isinstance(train, str):
        train = self.trains.index(train)

    if isinstance(departure_time, str):
        departure_time = hour_to_seconds(departure_time)

    if new_train_label in self.trains:
        raise ValueError(
            f"'{new_train_label}' is already used as a train label"
        )

    group, idx = self._train_schedule_group[
        self.trains[train]
    ]

    group_idx = _group_idx(self, group)

    new_train_schedule = \
        self.simulation['train_schedule_groups'][group_idx]['schedules'][idx].copy()  # noqa

    new_train_schedule['id'] = new_train_label
    new_train_schedule['departure_time'] = departure_time

    self.simulation['train_schedule_groups'][group_idx]['schedules'].append(
        new_train_schedule
    )

    with open(os.path.join(self.dir, self.simulation_json), "w") as outfile:
        json.dump(self.simulation, outfile)
