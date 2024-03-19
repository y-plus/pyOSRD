import base64
import copy
import os
import requests
import shutil

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import PIL

from PIL.JpegImagePlugin import JpegImageFile
from matplotlib.axes._axes import Axes


class Schedule(object):

    def __init__(self, num_blocks: int, num_trains: int):

        self._num_blocks = num_blocks
        self._num_trains = num_trains
        self._df = pd.DataFrame(
            columns=pd.MultiIndex.from_product(
                [range(self._num_trains), ['s', 'e']]
            ),
            index=range(num_blocks)
        )

    def __repr__(self) -> str:
        return str(self._df)

    @property
    def num_blocks(self) -> int:
        """Number of blocks"""
        return len(self._df)

    @property
    def blocks(self) -> list[int]:
        """list of blocks"""
        return self._df.index.to_list()

    @property
    def num_trains(self) -> int:
        """Number of trains"""
        return len(self._df.columns.levels[0])

    @property
    def trains(self) -> list[int]:
        """list of trains"""
        return getattr(
            self,
            '_trains',
            list(self._df.columns.levels[0])
        )

    @property
    def df(self) -> pd.DataFrame:
        """ Schedule as a pandas DataFrame"""
        return self._df

    def set(self, train, block, interval):
        """Set times for a train at a given block"""
        self._df.at[block, train] = interval

    @property
    def starts(self) -> pd.DataFrame:
        """Times when the trains enter the blocks"""
        return self._df.loc[
                pd.IndexSlice[:],
                pd.IndexSlice[:, 's']
            ].set_axis(self._df.columns.levels[0], axis=1).astype(float)

    @property
    def ends(self) -> pd.DataFrame:
        """Times when the trains leave the block"""
        return self._df.loc[
                pd.IndexSlice[:],
                pd.IndexSlice[:, 'e']
            ].set_axis(self._df.columns.levels[0], axis=1).astype(float)

    @property
    def durations(self) -> pd.DataFrame:
        """How much time do the train occupy the block"""
        return self.ends - self.starts

    def trajectory(self, train: int) -> list[int]:
        return list(
            self.starts[train][self.starts[train].notna()]
            .sort_values()
            .index
        )

    def previous_block(
        self,
        train: int,
        block: int | str,
    ) -> int | str | None:
        """"Previous block index in train's trajectory (None if 1st)

        Parameters
        ----------
        train : int
            Train index
        block : int | str
            Track section index (integer or string)

        Returns
        -------
        int | str | None
            Previous block index or None
        """
        t = self.trajectory(train)
        idx = list(t).index(block)

        if idx != 0:
            return t[idx-1]
        return None

    def next_block(
        self,
        train: int,
        block: int | str,
    ) -> int | str | None:
        """Next block index in train's trajectory (None if last)

        Parameters
        ----------
        train : int
            Train index
        block : int | str
            Block index (integer or string)

        Returns
        -------
        int | str | None
            Previous block index or None
        """

        t = self.trajectory(train)
        idx = list(t).index(block)

        if idx != len(t) - 1:
            return t[idx+1]
        return None

    def is_a_point_switch(
        self,
        train1: int,
        train2: int,
        block: int | str
    ) -> bool:
        """Given two trains trajectories, is the block a point switch ?

        Parameters
        ----------
        train1 : int
            first train index
        train2 : int
            second train index
        block : int | str
            Block index

        Returns
        -------
        bool
            True if it is point switch, False otherwise
            False if the block is not in the trajectory of
            one of the trains
        """
        if (
            block not in self.trajectory(train1)
            or
            block not in self.trajectory(train2)
        ):
            return False

        return (
            self.previous_block(train1, block)
            !=
            self.previous_block(train2, block)
            )

    def is_just_after_a_point_switch(
        self,
        train1: int,
        train2: int,
        block
    ) -> bool:
        """Given two trains, is the block just after a point switch ?

        Parameters
        ----------
        train1 : int
            first train index
        train2 : int
            second train index
        block : int | str
            Track section index

        Returns
        -------
        bool
            True if it is just after a point switch, False otherwise
            False if the block is not in the trajectory
            of one of the trains
        """
        if (
            block not in self.trajectory(train1)
            or
            block not in self.trajectory(train2)
        ):
            return False

        return (
            ~self.is_a_point_switch(train1, train2, block)
            and
            self.is_a_point_switch(
                train1,
                train2,
                self.previous_block(train1, block)
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
        block: int | str,
        delay: float
    ) -> 'Schedule':

        start = self._df.loc[block, (train, 's')]
        new_schedule = copy.deepcopy(self)

        # extend duration at given block
        new_schedule._df.loc[block, (train, 'e')] += delay

        # Add delay to all subsequent blocks
        new_schedule._df.loc[
            self._df[pd.IndexSlice[train, 's']] > start,
            pd.IndexSlice[train, :]
        ] += delay

        return new_schedule

    def shift_train_after(
        self,
        train1: int,
        train2: int,
        block: int | str
    ) -> 'Schedule':
        """Train1 waits until train 2 has freed block"""

        train1_waits_at = self.previous_block(train1, block)

        # If the block is the departure,
        # it has no previous block
        if train1_waits_at is None:
            train1_waits_at = block

        # If the conflict occurs at a switch point,
        # train 1 waits until the block
        # after the switch point is free
        if self.is_a_point_switch(train1, train2, block):
            block_shift = \
                self.next_block(train1, block)
        else:
            block_shift = block

        # if the conflict occurs just after a switch point,
        # train should wait before the switch
        if self.is_just_after_a_point_switch(train1, train2, block):
            train1_waits_at = \
                self.previous_block(train1, train1_waits_at)

        train1_wait_time = (
            self.ends.loc[block_shift, train2]
            - self.starts.loc[block_shift, train1]
        )

        new_schedule = self.add_delay(
            train1,
            train1_waits_at,
            train1_wait_time
        )

        if not new_schedule.is_a_point_switch(train1, train2, block):
            new_schedule._df.loc[block, (train1, 's')] = \
                self.ends.loc[block, train2]

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

    def first_conflict(self, train: int) -> tuple[int, int]:

        c = self.conflicts(train).stack()
        block, other_train = c.index[np.argmin(c)]
        return block, other_train

    def delays(self, ref_schedule: 'Schedule') -> pd.DataFrame:

        delta = self._df - ref_schedule._df

        return (
            delta.loc[pd.IndexSlice[:], pd.IndexSlice[:, 's']]
            .set_axis(self._df.columns.levels[0], axis=1)
            .astype(float)
        )

    def train_delay(self, train, ref_schedule: 'Schedule') -> pd.DataFrame:

        return self.delays(ref_schedule).max().loc[train]

    def compute_weighted_delays(
        self,
        ref_schedule,
        weights: pd.DataFrame
    ) -> float:
        """Compute an indicator to evaluate this Schedule.

        Compute an indicator based on the arrival times of the self
        compared to the ref_schedule ponderated by weights.

        The formula used is as follow ($s$ are all steps of the schedules,
        a step being a train in a zone):
            $$\sum_s [(delayed\_arrival - ref\_arrival)_s \times weight_s]$$

        Parameters
        ----------
        self: Schedule
            The delayed schedule, regulated use to compute the metric
        ref_schedule: Schedule
            The reference schedule used as the ideal schedule
        weights: pd.DataFrame
            The weights use to ponderate all delays

        Returns
        -------
        float
            The computed weighted delay
        """

        weighted_delays = self.delays(ref_schedule) * weights

        return weighted_delays.sum().sum()

    def total_delay_at_stations(
        self,
        ref_schedule,
        stations: list[int | str]
    ) -> float:

        weights = (
            self._df.loc[pd.IndexSlice[:], pd.IndexSlice[:, 's']]
            .set_axis(self._df.columns.levels[0], axis=1)
            .astype(float)
        ) * 0
        weights[weights.index.isin(stations)] = 1

        return self.compute_weighted_delays(ref_schedule, weights)

    def first_in(
        self,
        train1: int,
        train2: int,
        block: int | str
    ) -> int:
        """Among two trains, which train first arrives at a block"""

        trains_enter_at = (
            self.starts.loc[block, [train1, train2]].astype(float)
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
            block, other_train = self.first_conflict(train)
            action_needed = (
                self.is_a_point_switch(train, other_train, block)
                or
                self.is_just_after_a_point_switch(
                    train,
                    other_train,
                    block
                )
            )
        return action_needed

    @property
    def graph(self) -> nx.DiGraph:

        edges = set()
        for train, _ in enumerate(self.trains):
            traj = self.trajectory(train)
            edges = edges.union({
                (traj[i], traj[i+1])
                for i in range(len(traj)-1)
                })

        G = nx.DiGraph(edges)

        dict = {
            u: v
            for u, v in zip(
                self.df.index,
                self.df.infer_objects(copy=False).fillna(0).values
            )
        }

        nx.set_node_attributes(G, dict, 'times')

        return G

    @property
    def _mermaid_graph(self) -> str:
        return "graph LR;"+";".join([
            f"{str(edge[0]).replace('<','').replace('>','')}"
            f"-->{str(edge[1]).replace('<','').replace('>','')}"
            for edge in self.graph.edges
        ])

    def draw_graph(
        self,
        save: str | None = None,
    ) -> JpegImageFile:
        graphbytes = self._mermaid_graph.encode("ascii")
        base64_bytes = base64.b64encode(graphbytes)
        base64_string = base64_bytes.decode("ascii")
        url = "https://mermaid.ink/img/" + base64_string

        response = requests.get(url, stream=True)

        with open('tmp.png', 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        image = PIL.Image.open('tmp.png')

        if save:
            os.rename('tmp.png', save)
        else:
            os.remove('tmp.png')

        return image

    def propagate_delay(self, delayed_train: int) -> tuple[pd.DataFrame, int]:

        new_schedule = copy.deepcopy(self)
        decision = False
        while new_schedule.has_conflicts(delayed_train):
            decision = False
            if new_schedule.has_conflicts(delayed_train):

                block, other_train = \
                    new_schedule.first_conflict(delayed_train)
                decision = new_schedule.is_action_needed(delayed_train)

                if not decision:
                    first_in = new_schedule.first_in(
                        delayed_train,
                        other_train,
                        block
                    )
                    delayed_train = other_train \
                        if first_in == delayed_train else delayed_train
                    new_schedule = new_schedule.shift_train_after(
                        delayed_train,
                        first_in,
                        block
                    )
                else:
                    break
        return new_schedule, delayed_train

    def earliest_conflict(self) -> tuple[int | str, int]:
        """ Returns block where earliest conflict occurs,
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

    def sort(self) -> 'Schedule':
        """Sort the schedule index by occupancies times"""
        new_schedule = copy.deepcopy(self)
        sorted_idx = self.ends.max(axis=1).sort_values().index
        new_schedule ._df = new_schedule ._df.loc[sorted_idx]
        return new_schedule

    def plot(self, alpha: float = .5) -> Axes:

        s = copy.copy(self)
        s._df = s.df.dropna(axis=0, how='all')

        _, ax = plt.subplots()
        for train, label in enumerate(s.trains):
            ax.barh(
                width=s.durations[train],
                left=s.starts[train],
                y=s._df.index,
                label=str(label),
                height=1,
                alpha=alpha,
            )

        ax.set_xlabel('Time')
        ax.legend()

        return ax
