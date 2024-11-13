from typing import Callable
from pyosrd.groot import Groot

def evaluate_action(
    self: Groot,
    a: int,
    ref: Groot,
    scorer: Callable[[Groot, Groot], float],
) -> tuple[Groot, bool, bool, float]:
    
    train1, train2, zone, time = self.earliest_conflict()
    if not train1:
        return self, True, False, scorer(self, ref)
    train1, train2 = ref.trains_order_in_zone(train1, train2, zone)
    match a:
        case 0:  # keep order, wait at previous signal
            priority_train = train1
            waiting_train = train2
            wait_at = self.previous_signal(waiting_train, zone)
            r = self.make_train_wait(waiting_train, priority_train, wait_at, zone)
            valid = True
            done = not r.has_conflicts()
        case 1:  # keep order, wait at previous station
            priority_train = train1
            waiting_train = train2
            if not (wait_at := self.previous_station(waiting_train, zone)):
                return self, True, False, scorer(self, ref)
            r = self.make_train_wait(waiting_train, priority_train, wait_at, zone)
            valid = True
            done = not r.has_conflicts()    
        case 2:  # reroute second train
            if not (alt_zones := self.alternative_zones(train2, zone)):
                return self, True, False, scorer(self, ref)
            for alt_zones in alt_zones:
                if self.zones_are_free(
                    alt_zones[1:-1],
                    self.times_zones[train2][alt_zones[0]][0],
                    self.times_zones[train2][alt_zones[-1]][-1]
                ):
                    r = self.reroute(train2, alt_zones)
                    valid = True
                    done = not r.has_conflicts()
                    break
        case 3:  # modify order, wait at previous signal
            priority_train = train2
            waiting_train = train1
            cvg = self.previous_common_convergence(train1, train2, zone)
            if not cvg:
                return self, True, False, scorer(self, ref)
            
            wait_at = self.previous_signal(waiting_train, cvg)
            r = self.make_train_wait(waiting_train, priority_train, wait_at, zone)
            valid = True
            done = not r.has_conflicts()
        case 4:  # modify order, wait at previous station
            priority_train = train2
            waiting_train = train1
            cvg = self.previous_common_convergence(train1, train2, zone)
            if not cvg:
                return self, True, False, scorer(self, ref)
            if not (wait_at := self.previous_station(waiting_train, cvg)):
                return self, True, False, scorer(self, ref)
            r = self.make_train_wait(waiting_train, priority_train, wait_at, zone)
            valid = True
            done = not r.has_conflicts()    
        case 5:  # reroute first train
            if not (alt_zones := self.alternative_zones(train1, zone)):
                return self, True, False, scorer(self, ref)
            for alt_zones in alt_zones:
                if self.zones_are_free(
                    alt_zones[1:-1],
                    self.times_zones[train1][alt_zones[0]][0],
                    self.times_zones[train1][alt_zones[-1]][-1]
                ):
                    r = self.reroute(train1, alt_zones)
                    valid = True
                    done = not r.has_conflicts()
                    break
        case _:
            return None, None, None, None
    return r, done, valid, scorer(r, ref)
