from typing import Callable
from pyosrd.groot import Groot
from pyosrd.groot.objectives import sum_delays_at_end
from pyosrd.groot.rerouting import reroute_train_to_avoid_zone

def evaluate_action(
    self: Groot,
    a: int,
    ref: Groot,
    scorer: Callable[[Groot, Groot], float] = sum_delays_at_end,
    now: float = 0.,
) -> tuple[Groot, dict[str, str|float]]:

    train1, train2, zone, time = self.earliest_conflict()
    if not train1:
        return self, {
            'done': True,
            'valid': True,
            'score': scorer(self, ref)
        }
    try:
        train1, train2 = ref.trains_order_in_zone(train1, train2, zone)
    except KeyError:
        train1, train2 = self.trains_order_in_zone(train1, train2, zone)
    
    info = {"action": a}

    match a:
        case 0:  # keep order, wait at previous signal
            priority_train = train1
            waiting_train = train2
            wait_at = self.previous_signal(waiting_train, zone)
            if self.path_zones(waiting_train).index(zone) == 0:
                wait_at = zone
            r = self.make_train_wait(waiting_train, priority_train, wait_at, zone)
            tr1, tr2, _, t_new_conlict = r.earliest_conflict()
            done = t_new_conlict is None
            valid = True
            if not done:
                if t_new_conlict < time  and {tr1,tr2} == {train1, train2}:
                    valid = False
            info['conflict_at'] = zone
            info['priority_train'] = priority_train
            info['waiting_train'] = waiting_train
            info['wait_at'] = wait_at
            info['inversion'] = False


        case 1:  # keep order, wait at previous station
            priority_train = train1
            waiting_train = train2
            if not (wait_at := self.previous_station(waiting_train, zone)):
                return self, {
                    **info,
                    'done': True,
                    'valid': False,
                    'score': float('inf')
                }
            r = self.make_train_wait(waiting_train, priority_train, wait_at, zone)
            _, _, _, t_new_conlict = r.earliest_conflict()
            done = t_new_conlict is None
            valid = True
            # if not done:
            #     if t_new_conlict < time and {tr1,tr2} == {train1, train2}:
            #         valid = False
            info['conflict_at'] = zone
            info['priority_train'] = priority_train
            info['waiting_train'] = waiting_train
            info['wait_at'] = wait_at
            info['inversion'] = False

        case 2:  # reroute second train
            r = reroute_train_to_avoid_zone(
                self,
                train2,
                zone
            )
            if r is None:
                return self, {
                    **info,
                    'done': True,
                    'valid': False,
                    'score': float('inf') #scorer(self, ref)
                }
            valid = True
            done = not r.has_conflicts()
            info['conflict_at'] = zone
            info['rerouted_train'] = train2
            info['rerouted_tvds'] = [
                tvd for tvd in r.path(train2) if tvd not in self.path(train2)
            ]
            info['rerouted_zones'] = [
                r.zones[tvd] for tvd in info['rerouted_tvds']
            ]

        case 3:  # modify order, wait at previous signal
            priority_train = train2
            waiting_train = train1
            cvg = self.previous_common_convergence(train1, train2, zone)
            if not cvg:
                return self, {
                    **info,
                    'done': True,
                    'valid': False,
                    'score': float('inf')
                }

            wait_at = self.previous_signal(waiting_train, cvg)

            if self.times_zones[waiting_train][wait_at][1] < now:
                return self, {
                    **info,
                    'done': True,
                    'valid': False,
                    'score': float('inf')
                }

            r = self.make_train_wait(waiting_train, priority_train, wait_at, zone)
            tr1, tr2, _, t_new_conlict = r.earliest_conflict()
            done = t_new_conlict is None
            valid = True
            if not done:
                if t_new_conlict < time and {tr1, tr2} == {train1, train2}:
                    valid = False
            info['conflict_at'] = zone
            info['priority_train'] = priority_train
            info['waiting_train'] = waiting_train
            info['wait_at'] = wait_at
            info['inversion'] = True

        case 4:  # modify order, wait at previous station
            priority_train = train2
            waiting_train = train1
            cvg = self.previous_common_convergence(train1, train2, zone)

            if not cvg:
                return self, {
                    **info,
                    'done': True,
                    'valid': False,
                    'score': float('inf')
                }
            
            if not (wait_at := self.previous_station(waiting_train, cvg)):
                return self, {
                    **info,
                    'done': True,
                    'valid': False,
                    'score': float('inf')
                }
            
            if self.times_zones[waiting_train][wait_at][1] < now:
               return self, {
                    **info,
                    'done': True,
                    'valid': False,
                    'score': float('inf')
                }
            
            r = self.make_train_wait(waiting_train, priority_train, wait_at, zone)
            _, _, _, t_new_conlict = r.earliest_conflict()
            done = t_new_conlict is None
            valid = True
            if not done:
                if t_new_conlict < time:
                    valid = False
            info['conflict_at'] = zone
            info['priority_train'] = priority_train
            info['waiting_train'] = waiting_train
            info['wait_at'] = wait_at
            info['inversion'] = True

        case _:
            return None, info
    return r, {**info, 'done': done, 'valid': valid, 'score': scorer(r, ref)}
