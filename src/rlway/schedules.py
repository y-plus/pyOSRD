from typing import List, Tuple, Union, Dict
import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx


class Schedule(object):

    def __init__(self, num_track_sections: int, num_trains: int):

        self._num_track_sections = num_track_sections
        self._num_trains = num_trains
        self._df = pd.DataFrame(
            columns=pd.MultiIndex.from_product(
                [range(self._num_trains), ['s', 'e']]
            ),
            index=range(num_track_sections)
        )

    def __repr__(self) -> str:
        return str(self._df)

    @property
    def num_track_sections(self) -> int:
        """Number of track sections"""
        return len(self._df)

    @property
    def track_sections(self) -> List[int]:
        """List of track sections"""
        return self._df.index.to_list()

    @property
    def num_trains(self) -> int:
        """Number of trains"""
        return len(self._df.columns.levels[0])

    @property
    def trains(self) -> List[int]:
        """List of trains"""
        return list(self._df.columns.levels[0])

    @property
    def df(self) -> pd.DataFrame:
        """ Schedule as a pandas DataFrale"""
        return self._df

    def set(self, train, track, interval):
        """Set times for a train at a given track section"""
        self._df.at[track, train] = interval

    @property
    def starts(self) -> pd.DataFrame:
        """Times when the trains enter the track section"""
        return self._df.loc[
                pd.IndexSlice[:],
                pd.IndexSlice[:, 's']
            ].set_axis(self._df.columns.levels[0], axis=1).astype(float)

    @property
    def ends(self) -> pd.DataFrame:
        """Times when the trains leave the track section"""
        return self._df.loc[
                pd.IndexSlice[:],
                pd.IndexSlice[:, 'e']
            ].set_axis(self._df.columns.levels[0], axis=1).astype(float)

    @property
    def lengths(self) -> pd.DataFrame:
        """How much time do the train occupy the track section"""
        return self.ends - self.starts

    def trajectory(self, train: int) -> List[int]:
        return list(
            self.starts[train][self.starts[train].notna()]
            .sort_values()
            .index
        )

    def previous_track_section(
        self,
        train: int,
        track_section: Union[int, str],
    ) -> Union[int, str, None]:
        """"Previous track section index in train's trajectory (None if 1st)

        Parameters
        ----------
        train : int
            Train index
        track_section : Union[int, str]
            Track section index (integer or string)

        Returns
        -------
        Union[int, str, None]
            Previous track section index or None
        """
        t = self.trajectory(train)
        idx = list(t).index(track_section)

        if idx != 0:
            return t[idx-1]
        return None

    def next_track_section(
        self,
        train: int,
        track_section: Union[int, str],
    ) -> Union[int, str, None]:
        """Next track section index in train's trajectory (None if last)

        Parameters
        ----------
        train : int
            Train index
        track_section : Union[int, str]
            Track section index (integer or string)

        Returns
        -------
        Union[int, str, None]
            Previous track section index or None
        """

        t = self.trajectory(train)
        idx = list(t).index(track_section)

        if idx != len(t) - 1:
            return t[idx+1]
        return None

    def is_a_point_switch(
        self,
        train1: int,
        train2: int,
        track_section: Union[int, str]
    ) -> bool:
        """Given two trains trajectories, is the track section a point switch ?

        Parameters
        ----------
        train1 : int
            first train index
        train2 : int
            second train index
        track_section : Union[int, str]
            Track section index

        Returns
        -------
        bool
            True if it is point switch, False otherwise
            False if the track section is not in the trajectory of
            one of the trains
        """
        if (
            track_section not in self.trajectory(train1)
            or
            track_section not in self.trajectory(train2)
        ):
            return False

        return (
            self.previous_track_section(train1, track_section)
            !=
            self.previous_track_section(train2, track_section)
            )

    def is_just_after_a_point_switch(
        self,
        train1: int,
        train2: int,
        track_section
    ) -> bool:
        """Given two trains, is the track section just after a point switch ?

        Parameters
        ----------
        train1 : int
            first train index
        train2 : int
            second train index
        track_section : Union[int, str]
            Track section index

        Returns
        -------
        bool
            True if it is just after a point switch, False otherwise
            False if the track section is not in the trajectory
            of one of the trains
        """
        if (
            track_section not in self.trajectory(train1)
            or
            track_section not in self.trajectory(train2)
        ):
            return False

        return (
            ~self.is_a_point_switch(train1, train2, track_section)
            and
            self.is_a_point_switch(
                train1,
                train2,
                self.previous_track_section(train1, track_section)
            )
        )

    # actions

    def shift_train_departure(self, train: int, time: float) -> 'Schedule':
        """Shift the departure by a given time

        All the trajectory is shifted

        Parameters
        ----------
        train : int
            Train index
        time : float
            Departure's delay

        Returns
        -------
        Schedule
            The new schedule
        """

        new_schedule = copy.deepcopy(self)

        new_schedule._df[train] += time

        return new_schedule

    def add_delay(
        self,
        train: int,
        track_section: Union[int, str],
        delay: float
    ) -> 'Schedule':

        start = self._df.loc[track_section, (train, 's')]
        new_schedule = copy.deepcopy(self)

        # extend length at given track section
        new_schedule._df.loc[track_section, (train, 'e')] += delay

        # Add delay to all subsequent track sections
        new_schedule._df.loc[
            self._df[pd.IndexSlice[train, 's']] > start,
            pd.IndexSlice[train, :]
        ] += delay

        return new_schedule

    def shift_train_after(
        self,
        train1: int,
        train2: int,
        track_section: Union[int, str]
    ) -> 'Schedule':
        """Train1 waits until train has freed track_section"""

        train1_waits_at = self.previous_track_section(train1, track_section)

        # If the track section is the departure,
        # it has no previous track section
        if train1_waits_at is None:
            train1_waits_at = track_section

        # If the conflict occurs at a switch point,
        # train 1 waits until the track section
        # after the switch point is free
        if self.is_a_point_switch(train1, train2, track_section):
            track_section_shift = \
                self.next_track_section(train1, track_section)
        else:
            track_section_shift = track_section

        # if the conflict occurs just after a switch point,
        # train shoud wait before the switch
        if self.is_just_after_a_point_switch(train1, train2, track_section):
            train1_waits_at = \
                self.previous_track_section(train1, train1_waits_at)

        train1_wait_time = (
            self.ends.loc[track_section_shift, train2]
            - self.starts.loc[track_section_shift, train1]
        )

        new_schedule = self.add_delay(
            train1,
            train1_waits_at,
            train1_wait_time
        )

        if not new_schedule.is_a_point_switch(train1, train2, track_section):
            new_schedule._df.loc[track_section, (train1, 's')] = \
                self.ends.loc[track_section, train2]

        return new_schedule

    # conflicts_detection

    def conflicts(self, train: int) -> pd.DataFrame:

        starts0 = (
            pd.concat([self._df[train, 's']]*self.num_trains, axis=1)
            .set_axis(range(self.num_trains), axis=1)
        )
        ends0 = (
            pd.concat([self._df[train, 'e']]*self.num_trains, axis=1)
            .set_axis(range(self.num_trains), axis=1)
        )

        mask1 = self.ends >= starts0
        max_starts = (
            pd.concat([starts0, self.starts])
            .rename_axis('index')
            .groupby('index').max()
        )
        min_ends = (
            pd.concat([ends0, self.ends])
            .rename_axis('index')
            .groupby('index').min()
        )
        mask2 = max_starts < min_ends

        conflict_times = self.starts[mask1 & mask2].drop(columns=train)

        return (conflict_times[conflict_times.notna()])

    def has_conflicts(self, train: int) -> bool:

        return ~self.conflicts(train).isna().all().all()

    def first_conflict(self, train: int) -> Tuple[int, int]:

        c = self.conflicts(train).stack()
        track_section, other_train = c.index[np.argmin(c)]
        return track_section, other_train

    def delays(self, initial_schedule: 'Schedule') -> pd.DataFrame:

        delta = self._df - initial_schedule._df

        return (
            delta.loc[pd.IndexSlice[:], pd.IndexSlice[:, 's']]
            .set_axis(self._df.columns.levels[0], axis=1)
        )

    def total_delay_at_stations(
        self,
        initial_schedule,
        stations: List[Union[int, str]]
    ) -> float:

        try:
            return self.delays(initial_schedule).iloc[stations].sum().sum()
        except:
            return self.delays(initial_schedule).loc[stations].sum().sum()

    def first_in(
        self,
        train1: int,
        train2: int,
        track_section: Union[int, str]
    ) -> int:
        """Among two trains, which train first arrives at a track_section"""

        trains_enter_at = (
            self.starts.loc[track_section, [train1, train2]].astype(float)
        )

        trains = (
            trains_enter_at.index[trains_enter_at == trains_enter_at.min()]
            .to_list()
        )

        if len(trains) == 1:
            return trains[0]
        return trains

    def is_action_needed(self, train: int) -> bool:

        action_needed = False
        if self.has_conflicts(train):
            track_section, other_train = self.first_conflict(train)
            action_needed = (
                self.is_a_point_switch(train, other_train, track_section)
                or
                self.is_just_after_a_point_switch(
                    train,
                    other_train,
                    track_section
                )
            )
        return action_needed

    @property
    def graph(self) -> nx.DiGraph:

        edges = set()
        for train in self.trains:
            traj = self.trajectory(train)
            edges = edges.union({
                (traj[i], traj[i+1])
                for i in range(len(traj)-1)
                })

        G = nx.DiGraph(edges)

        dict = {
            u: v
            for u, v in zip(self.df.index, self.df.fillna(0).values)
        }

        nx.set_node_attributes(G, dict, 'times')

        return G

    def plot(self, alpha=.5):

        for train in self._df.columns.levels[0]:
            plt.barh(
                width=self.lengths[train],
                left=self.starts[train],
                y=self._df.index,
                label=train,
                height=1,
                alpha=alpha
                )
        plt.gca().invert_yaxis()
        plt.xlabel('Time')
        plt.ylabel('Track sections')
        plt.legend()

    def draw_graph(self):
        """

        https://networkx.org/documentation/stable/auto_examples/graph/plot_dag_layout.html
        """

        G = self.graph

        for layer, nodes in enumerate(nx.topological_generations(G)):
            # `multipartite_layout` expects the layer as a node attribute,
            # so add the numeric layer value as a node attribute
            for node in nodes:
                G.nodes[node]["layer"] = layer

        # Compute the multipartite_layout using the "layer" node attribute
        pos = nx.multipartite_layout(G, subset_key="layer")

        nx.draw_networkx(G, pos, node_shape='s')

    def propagate_delay(self, delayed_train: int) -> Tuple[pd.DataFrame, int]:

        new_schedule = copy.deepcopy(self)
        decision = False
        while new_schedule.has_conflicts(delayed_train):
            decision = False
            if new_schedule.has_conflicts(delayed_train):

                track_section, other_train = \
                    new_schedule.first_conflict(delayed_train)
                decision = new_schedule.is_action_needed(delayed_train)

                if not decision:
                    first_in = new_schedule.first_in(
                        delayed_train,
                        other_train,
                        track_section
                    )
                    delayed_train = other_train \
                        if first_in == delayed_train else delayed_train
                    new_schedule = new_schedule.shift_train_after(
                        delayed_train,
                        first_in,
                        track_section
                    )
                else:
                    break
        return new_schedule, delayed_train

    def sort(self) -> 'Schedule':
        """Sort the schedule index by occupancies times"""
        new_schedule = copy.deepcopy(self)
        sorted_idx = self.starts.min(axis=1).sort_values().index
        new_schedule ._df = new_schedule ._df.loc[sorted_idx]
        return new_schedule

    def earliest_conflict(self) -> Tuple[Union[int, str], int]:
        """ Returns track section where earliest conflict occurs,
        first train in and last in."""
        conflicts_times = [
            np.min(self.conflicts(train).stack())
            if not self.conflicts(train).stack().empty
            else np.inf
            for train in range(self.num_trains)
        ]

        if np.isfinite(np.min(conflicts_times)):
            other_train = np.argmin(conflicts_times)
            return (
                self.first_conflict(other_train)[0],
                self.first_conflict(other_train)[1],
                other_train
                )
        return None, None, None


def schedule_from_simulation(
        infra: Dict,
        res: List,
        simplify_route_names: bool = False,
        remove_bufferstop_to_bufferstop: bool = True,
) -> Schedule:

    useful_routes = [
        route
        for route in infra['routes']
        if not (('rt.buffer' in route['id']) and ('->buffer' in route['id']))
    ] if remove_bufferstop_to_bufferstop else [infra['routes']]

    routes = [
        route['id']
        for route in useful_routes
    ]

    s = Schedule(len(routes), len(res))

    routes_switches = {
        route['id']: list(route['switches_directions'].keys())[0]
        for route in useful_routes
        if len(list(route['switches_directions'].keys())) != 0
    }
    simulations = 'base_simulations'
    simulations = 'eco_simulations'

    for train in range(s.num_trains):
        route_occupancies = res[train][simulations][0]['route_occupancies']
        for route, times in route_occupancies.items():
            if route in routes:
                idx = routes.index(route)
                s._df.loc[idx, (train, 's')] = times['time_head_occupy']
                s._df.loc[idx, (train, 'e')] = times['time_tail_free']
    s._df.index = routes

    s._df.index = (
        pd.Series(s.df.index.map(routes_switches))
        .fillna(pd.Series(s.df.index))
    )

    s._df = s.df[~s.df.index.duplicated()]

    if simplify_route_names:
        s._df.index = (
            s.df.index
            .str.replace('rt.', '', regex=False)
            .str.replace('buffer_stop', 'STOP', regex=False)
        )

    return s
