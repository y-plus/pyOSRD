from typing import List

import numpy as np
import gymnasium as gym
from gymnasium import spaces

from pyosrd.schedules import Schedule


class RegulEnv(gym.Env):

    def __init__(
        self,
        schedule: Schedule,
        stations: List[int] = [],
        max_delay: float = 120.
    ):

        self._initial_schedule = schedule
        self._schedule = schedule
        self._stations = stations
        self._max_delay = max_delay
        self.observation_space = spaces.Dict({
            "timetable": spaces.Box(
                low=0,
                high=np.inf,
                shape=(schedule.num_blocks, 2*schedule.num_trains),
                dtype=np.float32,
            )
        })

        self.action_space = spaces.Discrete(2)

    def _get_obs(self):
        return {
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

    @property
    def done(self):
        return self._done

    @property
    def total_delay(self):
        return self._schedule.total_delay_at_stations(
            self._initial_schedule,
            self._stations
        )

    def reset(self, seed=None, train=None, track_section=None, delay=None):

        self._schedule = self._initial_schedule

        if train is None:
            train_with_delay = \
                self.np_random.integers(0, self.schedule.num_trains-1)
        else:
            train_with_delay = train

        if delay is None:
            delay = self.np_random.random() * self._max_delay

        if track_section is None:
            track = self.np_random.choice(
                self.schedule.trajectory(train_with_delay)
            )
        else:
            track = track_section

        self._schedule = \
            self._schedule.add_delay(train_with_delay, track, delay)
        self._schedule, train_with_delay = \
            self._schedule.propagate_delay(train_with_delay)

        self._done = self.schedule.earliest_conflict()[0] is None
        return self._get_obs(), {}

    def step(self, action):
        """ 0 = FIFO, 1 = LIFO """

        track_section, first_in, last_in = self._schedule.earliest_conflict()

        if action == 0:
            self._schedule = \
                self._schedule.shift_train_after(
                    last_in,
                    first_in,
                    track_section
                )
        else:
            self._schedule = \
                self._schedule.shift_train_after(
                    first_in,
                    last_in,
                    track_section
                )

        self._done = self.schedule.earliest_conflict()[0] is None

        if not self._done:
            reward = 0
        else:
            reward = - self.total_delay

        return self._get_obs(), reward, self._done, {}

    def render(self):
        self._schedule.plot()
