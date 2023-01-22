from typing import List, Tuple, Union
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
            columns=pd.MultiIndex.from_product([range(self._num_trains), ['s','e']]),
            index=range(num_track_sections)
        )

    def __repr__(self) -> str:
        return str(self._df)

    @property
    def num_track_sections(self) -> int:
        return len(self._df)

    @property
    def num_trains(self) -> int:
        return len(self._df.columns.levels[0])

    @property
    def trains(self) -> List[int]:
        return list(self._df.columns.levels[0])

    @property
    def track_sections(self) -> List[int]:
        return self._df.index.to_list()

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    def set(self, train, track, interval):
        self._df.at[track, train] = interval

    @property
    def starts(self) -> pd.DataFrame:
        return self._df.loc[
                pd.IndexSlice[:], 
                pd.IndexSlice[:,'s']
            ].set_axis(self._df.columns.levels[0], axis=1)

    @property
    def ends(self) -> pd.DataFrame:
        return self._df.loc[
                pd.IndexSlice[:], 
                pd.IndexSlice[:,'e']
            ].set_axis(self._df.columns.levels[0], axis=1)

    @property
    def lengths(self) -> pd.DataFrame:
        return self.ends - self.starts

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
    
    def trajectory(self, train: int) -> List[int]:
        return list(
            self.starts[train][self.starts[train].notna()]
            .sort_values()
            .index
        )

    def previous_track_section(self, train: int, track_section: int) -> Union[int, None]:


        t = self.trajectory(train)
        idx = list(t).index(track_section)

        if idx != 0:
            return t[idx-1]
        return None

    def next_track_section(self, train: int, track_section: int) -> int:

        t = self.trajectory(train)
        idx = list(t).index(track_section)

        if idx != len(t) - 1:
            return t[idx+1]
        return None

    def is_after_switch(self, train1: int, train2: int, track_section: int) -> bool:
        return (
            self.previous_track_section(train1, track_section) 
            !=
            self.previous_track_section(train2, track_section)
            )

    def add_delay(self, train: int, track_section: int, delay: float) -> 'Schedule':

        end = self._df.loc[track_section, (train, 'e')]
        new_schedule = copy.deepcopy(self)

        # extend length at given track section
        new_schedule._df.loc[track_section, (train, 'e')] += delay
        
        # Add delay to all subsequent track sections 
        new_schedule._df.loc[self._df[pd.IndexSlice[train,'s']]>=end, pd.IndexSlice[train,:]] += delay

        return new_schedule

    def conflicts(self, train: int) -> pd.DataFrame:

        starts0 =  (
            pd.concat([self._df[train,'s']]*self.num_trains, axis=1)
            .set_axis(range(self.num_trains), axis=1)
        )
        ends0 =  (
            pd.concat([self._df[train,'e']]*self.num_trains, axis=1)
            .set_axis(range(self.num_trains), axis=1)
        )

        mask1 = self.ends >= starts0
        mask2 = (
            pd.concat([starts0, self.starts]).rename_axis('index').groupby('index').max()
            < pd.concat([ends0, self.ends]).rename_axis('index').groupby('index').min()
            )

        conflict_times = self.starts[np.logical_and(mask1, mask2)].drop(columns=train)

        return (conflict_times[conflict_times.notna()])

    def has_conflicts(self, train: int) -> bool:

        return ~self.conflicts(train).isna().all().all()

    def first_conflict(self, train: int) -> Tuple[int, int]:

        c = self.conflicts(train).stack()
        track_section, other_train = c.index[np.argmin(c)]
        return track_section, other_train


    def shift_train_after(self, train1: int, train2: int, track_section: int) -> 'Schedule':
        """Train1 waits until train has freed track_section"""

        train1_waits_at = self.previous_track_section(train1, track_section)

        if train1_waits_at is None:
            train1_waits_at = track_section

        train1_wait_time = (
            self.ends.loc[track_section, train2]
            - self.starts.loc[track_section, train1]
        )

        new_schedule = self.add_delay(train1, train1_waits_at, train1_wait_time)

        if not new_schedule.is_after_switch(train1, train2, track_section):
            new_schedule._df.loc[track_section, (train1, 's')] = self.ends.loc[track_section, train2]
        
        return new_schedule

    def delays(self, initial_schedule: 'Schedule') -> pd.DataFrame:

        delta = self._df - initial_schedule._df

        return (
            delta.loc[pd.IndexSlice[:], pd.IndexSlice[:,'s']]
            .set_axis(self._df.columns.levels[0], axis=1)
        )

    def total_delay_at_stations(self, initial_schedule, stations: List[int]) -> float:

        return self.delays(initial_schedule).iloc[stations].sum().sum()

    def first_in(self, train1: int, train2: int, track_section: int) -> int:
        """Among two trains, which one train first arrives at a given track_section"""

        trains_enter_at = self.starts.loc[track_section, [train1, train2]].astype(float)
        
        trains = trains_enter_at.index[trains_enter_at==trains_enter_at.min()].to_list()

        if len(trains) == 1:
            return trains[0]
        return trains

    def is_action_needed(self, train: int) -> bool:

        action_needed = False
        if self.has_conflicts(train):
            track_section, other_train = self.first_conflict(train)
            action_needed = self.is_after_switch(train, other_train, track_section)
        return action_needed

    @property
    def graph(self) -> nx.DiGraph:

        edges = set()
        for train in self.trains:
            l = self.trajectory(train)
            edges = edges.union({(l[i], l[i+1]) for i in range(len(l)-1)})

        G = nx.DiGraph(edges)

        dict = {i: row for i, row in enumerate(self.df.fillna(0).values)}
        nx.set_node_attributes(G, dict, 'times')

        return G
 
    def draw_graph(self):

        G = self.graph
        pos = nx.planar_layout(G)
        nx.draw_networkx(G, pos)