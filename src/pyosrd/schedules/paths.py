def path(self, train: int | str) -> list[int | str]:
    """List of zones crossed by a given train

    Parameters
    ----------
    train : int | str
        Train index or label
    Returns
    -------
    list[int | str]
        List of zones
    """
    if isinstance(train, int):
        train = self.trains[train]

    return list(
        self.starts[train][self.starts[train].notna()]
        .sort_values()
        .index
    )


def previous_zone(
    self,
    train: int | str,
    zone: int | str,
) -> int | str | None:
    """"Previous zone index in train's path (None if 1st)

    Parameters
    ----------
    train : int | str
        Train index or label
    zone : int | str
        Track section index (integer or string)

    Returns
    -------
    int | str | None
        Previous zone index or None
    """

    t = self.path(train)
    idx = list(t).index(zone)

    if idx != 0:
        return t[idx-1]
    return None


def next_zone(
    self,
    train: int | str,
    zone: int | str,
) -> int | str | None:
    """Next zone index in train's path (None if last)

    Parameters
    ----------
    train : int
        Train index or label
    zone : int | str
        zone index (integer or string)

    Returns
    -------
    int | str | None
        Previous zone index or None
    """

    t = self.path(train)
    idx = list(t).index(zone)

    if idx != len(t) - 1:
        return t[idx+1]
    return None


def is_a_point_switch(
    self,
    train1: int | str,
    train2: int | str,
    zone: int | str
) -> bool:
    """Given two trains paths, is the zone a point switch ?

    Parameters
    ----------
    train1 : int | str
        first train index or label
    train2 : int | str
        second train index or label
    zone : int | str
        zone index

    Returns
    -------
    bool
        True if it is point switch, False otherwise.
        False if the zone is not in the path of
        one of the trains
    """
    if (
        zone not in self.path(train1)
        or
        zone not in self.path(train2)
    ):
        return False

    return (
        self.previous_zone(train1, zone)
        !=
        self.previous_zone(train2, zone)
        )


def is_just_after_a_point_switch(
    self,
    train1: int | str,
    train2: int | str,
    zone
) -> bool:
    """Given two trains, is the zone just after a point switch ?

    Parameters
    ----------
    train1 : int | str
        first train index or label
    train2 : int | str
        second train index or label
    zone : int | str
        Zone index

    Returns
    -------
    bool
        True if it is just after a point switch, False otherwise
        False if the zone is not in the path
        of one of the trains
    """
    if (
        zone not in self.path(train1)
        or
        zone not in self.path(train2)
    ):
        return False

    return (
        ~self.is_a_point_switch(train1, train2, zone)
        and
        self.is_a_point_switch(
            train1,
            train2,
            self.previous_zone(train1, zone)
        )
    )


def first_in(
    self,
    train1: int | str,
    train2: int | str,
    zone: int | str
) -> int:
    """Among two trains, which one first enters the zone"""

    if isinstance(train1, int):
        train1 = self.trains[train1]

    if isinstance(train2, int):
        train2 = self.trains[train2]

    trains_enter_at = (
        self.starts.loc[zone, [train1, train2]].astype(float)
    )

    trains = (
        trains_enter_at.index[trains_enter_at == trains_enter_at.min()]
        .to_list()
    )

    if len(trains) == 1:
        return trains[0]
    return trains


def trains_order_in_zone(
    self,
    train1: int | str,
    train2: int | str,
    zone: int | str
) -> list[int | str]:
    """Train ordering for a given zone

    Parameters
    ----------
    train1 : int | str
        First train index or label
    train2 : int | str
        Second train index or label
    zone : int | str
       Zone label

    Returns
    -------
    list[int | str]
        List of the trains in the order they cross the zone
    """
    if isinstance(train1, int):
        train1 = self.trains[train1]
    if isinstance(train2, int):
        train2 = self.trains[train2]
    order = self.starts.loc[zone].loc[[train1, train2]].sort_values()
    return order.dropna().index.tolist()


def previous_station(
    self,
    train: int | str,
    zone: int | str,
) -> str | None:
    """Previous station for given train and zone

    Parameters
    ----------
    train : int | str
        Train index or label
    zone : int | str
        Zone label

    Returns
    -------
    str | None
       Zone label for previous station
    """

    if isinstance(train, str):
        train = self.trains.index(train)

    if zone not in self.path(train=train):
        return

    idx = self.path(train=train).index(zone)

    zones = [
        z
        for z in self.path(train=train)[:idx][::-1]
        if self.step_type.loc[z, self.trains[train]] == 'station'
    ]

    if zones:
        return zones[0]
    return


def next_station(
    self,
    train: int | str,
    zone: int | str,
) -> str | None:
    """Next station for given train and zone

    Parameters
    ----------
    train : int | str
        Train index or label
    zone : int | str
        Zone label

    Returns
    -------
    str | None
       Zone label for next station
    """

    if isinstance(train, str):
        train = self.trains.index(train)

    if zone not in self.path(train=train):
        return

    idx = self.path(train=train).index(zone)

    zones = [
        z
        for z in self.path(train=train)[idx:]
        if self.step_type.loc[z, self.trains[train]] == 'station'
    ]

    if zones:
        return zones[-1]
    return


def previous_switch(
    self,
    train: int | str,
    zone: int | str,
) -> str | None:
    """Previous switch for given train and zone

    Parameters
    ----------
    train : int | str
        Train index or label
    zone : int | str
        Zone label

    Returns
    -------
    str | None
       Zone label for previous switch
    """

    if isinstance(train, str):
        train = self.trains.index(train)

    if zone not in self.path(train=train):
        return

    idx = self.path(train=train).index(zone)

    zones = [
        z
        for z in self.path(train=train)[:idx][::-1]
        if self.step_type.loc[z, self.trains[train]] == 'switch'
    ]

    if zones:
        return zones[0]
    return


def previous_switch_protecting_signal(
    self,
    train: int | str,
    zone: int | str,
) -> str | None:
    """Previous zone with a signal protecting a switch for given train and zone

    Parameters
    ----------
    train : int | str
        Train index or label
    zone : int | str
        Zone label

    Returns
    -------
    str | None
       Zone label with a signal protecting a switch
    """

    if isinstance(train, str):
        train = self.trains.index(train)

    if zone not in self.path(train=train):
        return

    idx = self.path(train=train).index(zone)

    if self.step_type.loc[zone, self.trains[train]] == 'switch':
        return previous_signal(self, train, zone)

    zones = [
        z
        for z in self.path(train=train)[:idx][::-1]
        if self.step_type.loc[z, self.trains[train]] == 'switch'
    ]

    if not zones:
        return
    return previous_signal(self, train, zones[0])


def previous_signal(
    self,
    train: int | str,
    zone: int | str,
) -> str | None:
    """Previous zone with a signal at its end for given train and zone

    Parameters
    ----------
    train : int | str
        Train index or label
    zone : int | str
        Zone label

    Returns
    -------
    str | None
       Zone label with a signal at its end
    """

    if isinstance(train, str):
        train = self.trains.index(train)

    if zone not in self.path(train=train):
        return

    idx = self.path(train=train).index(zone)

    zones = [
        z
        for z in self.path(train=train)[:idx][::-1]
        if self.step_type.loc[z, self.trains[train]] in ['signal', 'station']
    ]

    if zones:
        return zones[0]
    return


@property
def stations(self) -> list[str]:
    """List of zones corresponding to a station"""
    return (
        self
        .step_type[self.step_type == 'station']
        .dropna(how='all')
        .index
        .tolist()
    )
