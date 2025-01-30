import copy
import json
import os
import shutil

from pyosrd.osrd import Point
from pyosrd.utils import hour_to_seconds


def add_delay(
    self,
    train: int | str,
    time_threshold: float | str,
    delay: float,
) -> None:
    """Add delay to a train for t > time_threshold"

    Parameters
    ----------
    train : int | str
        Train index or label
    time_threshold : float | str
        Time before which the train is not delayed, given
        either in seconds or in time format "hh:mm:ss"
    delay : float
       Delay in seconds applied after time threshold
    """

    try:
        with open(os.path.join(self.dir, self.delays_json), 'r') as f:
            delays = json.load(f)
    except FileNotFoundError:
        delays = []

    if isinstance(time_threshold, str):
        time_threshold = hour_to_seconds(time_threshold)

    if isinstance(train, int):
        train = self.trains[train]

    delays += [
        {
            "train_id": train,
            "time_threshold": time_threshold,
            "delay": delay,
        }
    ]

    with open(os.path.join(self.dir, 'delays.json'), "w") as outfile:
        json.dump(delays, outfile)


def add_delay_at_station(
    self,
    train: int | str,
    station: str,
    delay: float = 0
) -> None:

    points = self.points_encountered_by_train(train, types=['detector', 'station'])
    for i, st in enumerate(points):
        if "".join(st['id'].split('/')[:-1])==station:
            d1, d2 = points[i-1], points[i+1]
            t = (d1['t_base']+d2['t_base'])/2
            self.add_delay(train, t, delay)

def add_delays_in_results(self) -> None:

    try:
        with open(os.path.join(self.dir, self.delays_json), 'r') as f:
            delays = json.load(f)
    except FileNotFoundError:
        delays = []
    delays.sort(key=lambda x: x['time_threshold'])
    for train in self.trains:
        previous_delays = 0
        for d in [delay for delay in delays if delay['train_id']==train]:
            train_id = d['train_id']
            time_threshold = d['time_threshold'] + previous_delays
            delay = d['delay']
            previous_delays += delay
            gr, idx = self._train_schedule_group[
                train_id
            ]

            for eco_or_base in ['eco', 'base']:
                sim = f'{eco_or_base}_simulations'

                dict = (
                    self.results[gr][sim][idx]
                    if self.results[gr][sim][idx] is not None
                    else {}
                )
                for key, records in dict.items():
                    if isinstance(records, list):
                        for i, record in enumerate(records):
                            for subkey, value in record.items():
                                if 'time' in subkey and time_threshold == 0:
                                    self.results[gr][sim][idx][key][i][subkey] += \
                                        delay
                                elif 'time' in subkey and value > time_threshold:
                                    self.results[gr][sim][idx][key][i][subkey] += \
                                        delay
                    if key == 'head_positions' and time_threshold > 0:
                        position = None
                        for i, record in enumerate(records):
                            if record['time'] > time_threshold :
                                position = i - 1
                                break
                        if position:
                            records.insert(
                                position+1,
                                    {
                                        'offset': records[position]['offset'],
                                        'path_offset':  records[position]['path_offset'],
                                        'time': records[position]['time'] + delay,
                                        'track_section':  records[position]['track_section'],
                                    }
                            )

    with open(os.path.join(self.dir, self.results_json), "w") as outfile:
        json.dump(self.results, outfile)


def delayed(self):

    delayed = copy.deepcopy(self)
    name = 'delayed'

    delayed.results_json = os.path.join(name, self.results_json)

    directory = os.path.join(self.dir, name)
    if not os.path.exists(directory):
        os.mkdir(directory)

    delayed.add_delays_in_results()

    return delayed


def reset_delays(self) -> None:
    if os.path.exists(os.path.join(self.dir, 'delayed')):
        shutil.rmtree(os.path.join(self.dir, 'delayed'))
    if os.path.exists(os.path.join(self.dir, self.delays_json)):
        os.remove(os.path.join(self.dir, self.delays_json))


def add_delay_between_points(
    self,
    train: int | str,
    point_id_A: str,
    point_id_B: str,
    delay: float,
) -> None:

    if isinstance(train, str):
        train = self.trains.index(train)

    points = [
        p
        for p in self.points_encountered_by_train(train)
        if p['type'] in ['detector', 'departure', 'arrival']
    ]


    pointA = next(
        (p for p in points if p['id'] == point_id_A),
        None
    )
    
    pointB = next(
        (p for p in points if p['id'] == point_id_B),
        None
    )
    if pointB is None or pointA is None:
        return

    group, idx = self._train_schedule_group[
        self.trains[train]
    ]

    
    
    stops = self.get_stops(train)
    for stop in stops:
        if 'position' not in stop:
            stop['position'] = self.offset_in_path_of_train(
                Point(
                    track_section=stop['location']['track_section'],
                    position=stop['location']['offset'],
                ),
                train
            )

    for eco_or_base in ['base', 'eco']:

        if self.results[group][ f'{eco_or_base}_simulations'] == [None]:
            break

        limits = sorted(
            [pointA, pointB],
            key=lambda x: x[f"t_{eco_or_base}"]
        )

        t_in, t_out = limits[0][f"t_{eco_or_base}"], limits[1][f"t_{eco_or_base}"]
        pos_in, pos_out = limits[0]['offset'], limits[1]['offset']

        TIME_TO_STOP = 60  # seconds

        detector = next(
            (
                d for d in self.infra['detectors']
                if d['id'] == limits[1]['id']
            ),
            None
        )

        if detector:
            self._head_position(train, eco_or_base).append(
                {
                    'time': t_out,
                    'offset': detector['position'],
                    'path_offset': pos_out,
                    "track_section": detector['track'],
                }
            )

            self._head_position(train, eco_or_base).sort(
                key=lambda r: r['time']
            )



        stop = next(
            (
                s for s in stops
                if s['position'] >= pos_in and s['position'] < pos_out
            ),
            None
        )

        if stop:
            for i, r in enumerate(h:= self._head_position(train, eco_or_base)):
                if r['path_offset'] > stop['position']:
                    r['time'] += delay

        elif delay <= 2 * TIME_TO_STOP:
            stretch = (t_out - t_in + delay)/(t_out-t_in)
            for r in self._head_position(train, eco_or_base):
                if r['time'] >= t_in and r['time'] < t_out:
                    r['time'] = t_in + (r['time'] - t_in) * stretch
                elif r['time'] >= t_out:
                    r['time'] += delay
        else:
            for i, r in enumerate(h:= self._head_position(train, eco_or_base)):
                if r['time'] > t_out and h[i-1]['time'] > t_out:
                    r['time'] += delay
                elif r['time'] >= t_out and h[i-1]['time'] < t_out:
                    r['time'] += delay - TIME_TO_STOP
                    h[i-1]['time'] += TIME_TO_STOP
                    r['path_offset'] = h[i-1]['path_offset']
                    r['offset'] =  h[i-1]['offset']
                    r['track_section'] =  h[i-1]['track_section']


def shift_train_departure(
    self,
    train: int | str,
    delay: float,
) -> None:
    
    if isinstance(train, str):
        train = self.trains.index(train)

    group, idx = self._train_schedule_group[
        self.trains[train]
    ]

    for eco_or_base in ['base', 'eco']:

        if self.results[group][ f'{eco_or_base}_simulations'] == [None]:
            break

        for r in self._head_position(train, eco_or_base):
                r['time'] += delay


