import copy

import gymnasium as gym
import networkx as nx
import pandas as pd

from gymnasium import spaces
from ortools.linear_solver import pywraplp

from pyosrd.schedules import Schedule
from pyosrd.agents.scheduler_agent import SchedulerAgent
from pyosrd.utils import seconds_to_hour

DISPATCH_OPTIONS = [
    {'priority': 0, 'wait_at': 'previous_signal'},
    {'priority': 0, 'wait_at': 'previous_switch_protecting_signal'},
    {'priority': 0, 'wait_at': 'previous_station'},
    # {'priority': 1, 'wait_at': 'previous_signal'},
    {'priority': 1, 'wait_at': 'previous_switch_protecting_signal'},
    {'priority': 1, 'wait_at': 'previous_station'},
]


def apply_dispatch_option(
    schedule,
    option: dict,
    ref_schedule: Schedule,
    n_blocks_between_trains: int = 0,
    switch_change_delay: float = 0,
):

    first_zone, train1, train2 = schedule.with_interlocking_constraints(
        n_blocks_between_trains=n_blocks_between_trains,
        switch_change_delay=switch_change_delay
    ).earliest_conflict()

    if not first_zone:
        return schedule, -1, -1

    trains = ref_schedule.trains_order_in_zone(train1, train2, first_zone)

    priority_train_idx, zone_fn = option.values()
    priority_train = trains[priority_train_idx]
    other_train = trains[1-priority_train_idx]

    new_schedule = copy.deepcopy(schedule)
    still_conflicted = True

    while still_conflicted:

        zone = new_schedule.with_interlocking_constraints(
                n_blocks_between_trains=n_blocks_between_trains,
                switch_change_delay=switch_change_delay
            ).first_conflict_zone(train1, train2)
        starts = new_schedule.starts
        after_conflict = new_schedule.start_from(
            min(
                starts.loc[
                    new_schedule.previous_zone(priority_train, zone),
                    priority_train
                ],
                starts.loc[
                    new_schedule.previous_zone(other_train, zone),
                    other_train
                ]
            )
        ) if new_schedule.path(priority_train).index(zone) != 0\
            else new_schedule

        if (
            zone_fn in ['previous_signal', 'previous_station']
            and new_schedule.path(other_train).index(zone) == 0
        ):

            new_schedule = new_schedule.shift_train_departure(
                other_train,
                (
                    new_schedule.ends.loc[
                        zone,
                        priority_train
                    ] - starts.loc[zone, other_train]
                )
            )

            new_schedule = speeds_up_to_catch_up(
                new_schedule,
                other_train,
                zone,
                priority_train,
                ref_schedule
            )

        elif wait_at := getattr(after_conflict, zone_fn)(other_train, zone):
            # TODO: Définition de wait_at remonter avant la boucle while ?
            if new_schedule.is_a_point_switch(
                priority_train,
                other_train,
                zone,
            ):
                zone_to_free = new_schedule.next_zone(other_train, zone)
            else:
                zone_to_free = zone
            new_schedule = new_schedule.set_priority_train(
                priority_train,
                other_train,
                wait_at,
                zone_to_free,
                n_blocks_between_trains=n_blocks_between_trains,
                switch_change_delay=switch_change_delay,
            )

            new_schedule = speeds_up_to_catch_up(
                new_schedule,
                other_train,
                zone,
                priority_train,
                ref_schedule
            )
        else:
            new_schedule = schedule
            break

        still_conflicted = new_schedule.with_interlocking_constraints(
            n_blocks_between_trains=n_blocks_between_trains,
            switch_change_delay=switch_change_delay
        ).are_conflicted(priority_train, other_train)

    return new_schedule, priority_train, other_train


def speeds_up_to_catch_up(
    schedule: Schedule,
    train: int | str,
    action_zone: str,
    priority_train: int | str,
    ref_schedule: Schedule
) -> Schedule:

    if isinstance(train, int):
        train = schedule.trains[train]

    if isinstance(priority_train, int):
        priority_train = schedule.trains[priority_train]

    new_schedule = copy.deepcopy(schedule)
    solver = pywraplp.Solver.CreateSolver("GLOP")
    if not solver:
        return

    if next_station := schedule.next_station(train, action_zone):
        path = schedule.path(train)
        zones = path[path.index(action_zone):path.index(next_station)+1]
        t_in, t_out = dict(), dict()
        mins_t_in = schedule.ends[priority_train].to_dict()
        min_durations = schedule.min_durations[train].to_dict()
        starts = schedule.starts[train].to_dict()
        ends = schedule.ends[train].to_dict()

        for i, zone in enumerate(zones):
            t_in[zone] =\
                solver.NumVar(mins_t_in[zone], solver.infinity(), f"t_in_{zone}")
            t_out[zone] = solver.NumVar(0, solver.infinity(), f"t_out_{zone}")
            solver.Add(t_out[zone] - t_in[zone] >= min_durations[zone])
            if i > 0:
                previous_zone = zones[zones.index(zone)-1]
                solver.Add(
                    t_in[zone] ==
                    t_out[previous_zone]
                    - (ends[previous_zone] - starts[zone])
                )
            if zone == path[0]:
                solver.Add(
                    t_in[zone] == t_out[zone] - (ends[zone] - starts[zone])
                )
        solver.Minimize(t_in[zones[-1]])
        status = solver.Solve()

        if status == pywraplp.Solver.OPTIMAL:
            new_times = pd.DataFrame(
                    {
                        's': [t_in[z].solution_value() for z in zones],
                        'e': [t_out[z].solution_value() for z in zones]
                    },
                    index=zones
                )
            new_schedule._df.loc[zones, train] = new_times.values

    return new_schedule


class TrainsDispatchingEnv(gym.Env):

    def __init__(
        self,
        ref_schedule,
        delayed_schedule,
        n_blocks_between_trains: int = 0,
        switch_change_delay: float = 0,
    ):
        self._ref_schedule = ref_schedule
        self._delayed_schedule = delayed_schedule
        self._schedule = delayed_schedule
        self._stations = self._schedule.stations
        self._n_blocks_between_trains = n_blocks_between_trains
        self._switch_change_delay = switch_change_delay

        self.action_space = spaces.Discrete(len(DISPATCH_OPTIONS))

    @property
    def schedule(self) -> Schedule:
        return self._schedule

    @property
    def ref_schedule(self) -> Schedule:
        return self._ref_schedule

    @property
    def stations(self):
        return self._stations

    @stations.setter
    def stations(self, station_names: list[str]) -> None:
        self._stations = station_names

    def calculate_reward(self):
        total_delay = 0
        for train in self._schedule.trains:
            last_zone = self._schedule.path(train)[-1]
            total_delay += (
                self._schedule.ends.loc[last_zone, train]
                - self._delayed_schedule.ends.loc[last_zone, train]
            )
        return -total_delay

    def reset(self):
        self._schedule = self._delayed_schedule

    @property
    def state(self) -> int:
        return self._schedule

    def set_state(self, schedule: Schedule):
        self._schedule = schedule

    def step(self, action: int):
        self._schedule, priority_train, other_train = apply_dispatch_option(
            self._schedule,
            option=DISPATCH_OPTIONS[action],
            ref_schedule=self._ref_schedule,
            n_blocks_between_trains=self._n_blocks_between_trains,
            switch_change_delay=self._switch_change_delay,
        )

        self._done = self._schedule.no_conflict()
        reward = self.calculate_reward()

        info = {
            'priority_train': priority_train,
            'other_train': other_train
        }

        return self._schedule, reward, self._done, info

    def render(self):
        self._schedule.plot()


def branch_and_cut(
    env: gym.Env,
    max_successive_actions: int | None = None,
    explore_all_branches: bool = False,
) -> tuple[nx.DiGraph, int, float]:

    def explore_node_recursive(
        nodes_to_explore,
        max_reward,
        node,
        done,
        max_node
    ):

        if node in nodes_to_explore:
            all_actions_evaluated = \
                len(list(tree.successors(node))) == env.action_space.n

            if max_successive_actions is not None:
                max_successive_actions_reached = (
                    len(nx.shortest_path(tree, source=0, target=node))
                    > max_successive_actions
                )
            else:
                max_successive_actions_reached = False

            reward = tree.nodes[node]['reward']
            if done and reward >= max_reward:
                max_reward, max_node = reward, node
            not_better = reward < max_reward and node > 0

            if explore_all_branches:
                not_better = False

            if (
                all_actions_evaluated
                or max_successive_actions_reached
                or done
                or not_better
            ):
                nodes_to_explore.remove(node)
                next_node =\
                    nx.ancestors(tree, node).intersection(nodes_to_explore)

                if next_node:
                    env.set_state(tree.nodes.get(max(next_node))['state'])
                    explore_node_recursive(
                        nodes_to_explore,
                        max_reward,
                        max(next_node),
                        False,
                        max_node
                    )
            else:
                new_node_index = tree.number_of_nodes()
                action = len(list(tree.successors(node)))
                _, new_reward, done, info = env.step(action)
                valid = True
                if new_reward == tree.nodes[node]['reward']:
                    done = True
                    valid = False
                tree.add_node(
                    new_node_index,
                    state=env.state,
                    reward=new_reward,
                    done=done,
                    valid=valid
                )
                tree.add_edge(
                    node,
                    new_node_index,
                    action=len(list(tree.successors(node))),
                    priority_train=info['priority_train'],
                    other_train=info['other_train'],
                )
                nodes_to_explore.add(new_node_index)
                explore_node_recursive(
                    nodes_to_explore,
                    max_reward,
                    new_node_index,
                    done,
                    max_node
                )

    env.reset()
    tree = nx.DiGraph()
    tree.add_node(
        0,
        state=env.state,
        reward=env.calculate_reward(),
        done=False,
        valid=True
    )

    nodes_to_explore = set()
    nodes_to_explore.add(0)

    explore_node_recursive(
        nodes_to_explore,
        float('-inf'),
        node=0,
        done=False,
        max_node=0
    )
    rewards = [
        (node, tree.nodes[node]['reward'])
        for node in tree.nodes
        if tree.nodes[node]['done'] and tree.nodes[node]['valid']
    ]
    best_node, best_reward = sorted(
        rewards,
        key=lambda x: -x[1]
    )[0]
    env.set_state(tree.nodes[best_node]['state'])
    return tree, best_node, best_reward


class DecisionTreeAgent(SchedulerAgent):

    n_blocks_between_trains: int = 0
    switch_change_delay: int = 0

    def build_gym_env(self) -> gym.Env:
        self._env = TrainsDispatchingEnv(
            ref_schedule=self.ref_schedule,
            delayed_schedule=self.delayed_schedule,
            n_blocks_between_trains=self.n_blocks_between_trains,
            switch_change_delay=self.switch_change_delay
        )

    @property
    def regulated_schedule(self) -> Schedule:
        self.build_gym_env()
        self._env.reset()
        tree, best_node, best_reward = branch_and_cut(
            self._env,
            max_successive_actions=None
        )

        print(
            f"{seconds_to_hour(-int(best_reward))} found at {best_node}"
            f" in {len(tree.nodes)} evaluations"
        )
        sp = nx.shortest_path(tree, 0, best_node)
        pg = nx.path_graph(sp)  # does not pass edges attributes

        # Read attributes from each edge
        for ea in pg.edges():
            # print from_node, to_node, edge's attributes
            print(
                f"{ea[0]} -> {ea[1]}",
                tree.edges[ea[0], ea[1]]['action'],
                tree.edges[ea[0], ea[1]]['priority_train'],
                tree.edges[ea[0], ea[1]]['other_train'],
            )

        return tree.nodes.get(best_node)['state']


class PropagationAgent(SchedulerAgent):

    n_blocks_between_trains: int = 0
    switch_change_delay: int = 0

    def build_gym_env(self) -> gym.Env:
        self._env = TrainsDispatchingEnv(
            ref_schedule=self.ref_schedule,
            delayed_schedule=self.delayed_schedule,
            n_blocks_between_trains=self.n_blocks_between_trains,
            switch_change_delay=self.switch_change_delay
        )

    @property
    def regulated_schedule(self) -> Schedule:
        self.build_gym_env()
        self._env.reset()
        done = self._env._schedule.no_conflict()

        while not done:
            _, reward, done, info = self._env.step(0)
        
        return self._env._schedule

