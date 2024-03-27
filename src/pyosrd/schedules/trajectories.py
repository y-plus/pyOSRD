def trajectory(self, train: int) -> list[int]:
    return list(
        self.starts[train][self.starts[train].notna()]
        .sort_values()
        .index
    )


def previous_zone(
    self,
    train: int,
    zone: int | str,
) -> int | str | None:
    """"Previous zone index in train's trajectory (None if 1st)

    Parameters
    ----------
    train : int
        Train index
    zone : int | str
        Track section index (integer or string)

    Returns
    -------
    int | str | None
        Previous zone index or None
    """
    t = self.trajectory(train)
    idx = list(t).index(zone)

    if idx != 0:
        return t[idx-1]
    return None


def next_zone(
    self,
    train: int,
    zone: int | str,
) -> int | str | None:
    """Next zone index in train's trajectory (None if last)

    Parameters
    ----------
    train : int
        Train index
    zone : int | str
        zone index (integer or string)

    Returns
    -------
    int | str | None
        Previous zone index or None
    """

    t = self.trajectory(train)
    idx = list(t).index(zone)

    if idx != len(t) - 1:
        return t[idx+1]
    return None


def is_a_point_switch(
    self,
    train1: int,
    train2: int,
    zone: int | str
) -> bool:
    """Given two trains trajectories, is the zone a point switch ?

    Parameters
    ----------
    train1 : int
        first train index
    train2 : int
        second train index
    zone : int | str
        zone index

    Returns
    -------
    bool
        True if it is point switch, False otherwise.
        False if the zone is not in the trajectory of
        one of the trains
    """
    if (
        zone not in self.trajectory(train1)
        or
        zone not in self.trajectory(train2)
    ):
        return False

    return (
        self.previous_zone(train1, zone)
        !=
        self.previous_zone(train2, zone)
        )


def is_just_after_a_point_switch(
    self,
    train1: int,
    train2: int,
    zone
) -> bool:
    """Given two trains, is the zone just after a point switch ?

    Parameters
    ----------
    train1 : int
        first train index
    train2 : int
        second train index
    zone : int | str
        Zone index

    Returns
    -------
    bool
        True if it is just after a point switch, False otherwise
        False if the zone is not in the trajectory
        of one of the trains
    """
    if (
        zone not in self.trajectory(train1)
        or
        zone not in self.trajectory(train2)
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
    train1: int,
    train2: int,
    zone: int | str
) -> int:
    """Among two trains, which one first enters the zone"""

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
