from typing import List

import numpy as np
import gymnasium as gym
from gymnasium import spaces

from schedules import Schedule

class RegulEnv(gym.Env):
    
    def __init__(self, schedule: Schedule, stations: List[int] = [], max_delay: float = 2.):

        self._initial_schedule = schedule
        self._schedule = schedule
        self._stations = stations
        self._max_delay = max_delay
        self.observation_space = spaces.Dict({
            "delayed_train" : spaces.Box(0, self._schedule.num_trains-1, dtype=int),
            "timetable": spaces.Box(
                low=0,
                high=np.inf,
                shape=(schedule.num_track_sections, 2*schedule.num_trains),
                dtype=np.float32,
            )
        })  

        self.action_space = spaces.Discrete(2)

    def _get_obs(self):
        return {
            "delayed_train": self._delayed_train,
            "timetable": self._schedule.df.values
        }

    @property
    def schedule(self) -> Schedule:
        return self._schedule

    @property
    def initial_schedule(self) -> Schedule:
        return self._initial_schedule

    @property
    def stations(self):
        return self._stations

    def reset(self, seed=None, train=None, track_section=None, delay=None):

        self._schedule = self._initial_schedule
        self._delayed_train = 0

        while not self._schedule.has_conflicts(self._delayed_train): # to ensure a schedule with conflicts
            self._delayed_train = self.np_random.integers(0, self.schedule.num_trains-1) if train is None else train
            delay = self.np_random.random() * self._max_delay if delay is None else delay
            track = self.np_random.choice(self.schedule.trajectory(self._delayed_train)) if track_section is None else track_section

            self._schedule = self._schedule.add_delay(self._delayed_train, track, delay)
            self._schedule, self._delayed_train = self._schedule.propagate_delay(self._delayed_train)

        return self._get_obs(), {}

    def step(self, action):
        """
        0: the delayed train waits before the switch for the track section to be free
        1: the delayed train has the priority, the other waits
        """

        track_section, other_train = self._schedule.first_conflict(self._delayed_train)
        if action == 0: # delayed train waits
            first_out, last_out = other_train, self._delayed_train
        else: # delayed train has priority
            first_out, last_out = self._delayed_train, other_train
        self._schedule = self._schedule.shift_train_after(last_out, first_out, track_section)
        self._delayed_train = last_out
        self._schedule, self._delayed_train = self._schedule.propagate_delay(last_out)


        if self._schedule.has_conflicts(self._delayed_train):
            done = False
            reward = 0
        else:
            done = True
            reward = - self._schedule.total_delay_at_stations(
                self._initial_schedule, 
                self._stations
                )

        return self._get_obs(), reward, done, {}


    def render(self):
        self._schedule.plot()
    