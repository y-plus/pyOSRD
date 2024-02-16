import copy
import json
import os
import shutil


def add_delay(
    self,
    train_id: str,
    time_threshold: float,
    delay: float,
) -> None:

    try:
        with open(os.path.join(self.dir, self.delays_json), 'r') as f:
            delays = json.load(f)
    except FileNotFoundError:
        delays = []

    delays += [
        {
            "train_id": train_id,
            "time_threshold": time_threshold,
            "delay": delay,
        }
    ]

    with open(os.path.join(self.dir, 'delays.json'), "w") as outfile:
        json.dump(delays, outfile)


def add_delays_in_results(self) -> None:

    try:
        with open(os.path.join(self.dir, self.delays_json), 'r') as f:
            delays = json.load(f)
    except FileNotFoundError:
        delays = {}

    for d in delays:
        train_id = d['train_id']
        time_threshold = d['time_threshold']
        delay = d['delay']

        gr, idx = self._train_schedule_group[
            train_id
        ]

        for eco_or_base in ['eco', 'base']:
            sim = f'{eco_or_base}_simulations'

            dict = (
                self.results[gr][sim][idx]
                if self.results[gr][sim] != [None]
                else {}
            )
            for key, records in dict.items():
                if isinstance(records, list):
                    for i, record in enumerate(records):
                        for subkey, value in record.items():
                            if 'time' in subkey and value > time_threshold:
                                self.results[gr][sim][idx][key][i][subkey] += \
                                    delay

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
