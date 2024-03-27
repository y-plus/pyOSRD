def trajectory(self, train: int) -> list[int]:
    return list(
        self.starts[train][self.starts[train].notna()]
        .sort_values()
        .index
    )


def previous_block(
    self,
    train: int,
    block: int | str,
) -> int | str | None:
    """"Previous block index in train's trajectory (None if 1st)

    Parameters
    ----------
    train : int
        Train index
    block : int | str
        Track section index (integer or string)

    Returns
    -------
    int | str | None
        Previous block index or None
    """
    t = self.trajectory(train)
    idx = list(t).index(block)

    if idx != 0:
        return t[idx-1]
    return None


def next_block(
    self,
    train: int,
    block: int | str,
) -> int | str | None:
    """Next block index in train's trajectory (None if last)

    Parameters
    ----------
    train : int
        Train index
    block : int | str
        Block index (integer or string)

    Returns
    -------
    int | str | None
        Previous block index or None
    """

    t = self.trajectory(train)
    idx = list(t).index(block)

    if idx != len(t) - 1:
        return t[idx+1]
    return None


def is_a_point_switch(
    self,
    train1: int,
    train2: int,
    block: int | str
) -> bool:
    """Given two trains trajectories, is the block a point switch ?

    Parameters
    ----------
    train1 : int
        first train index
    train2 : int
        second train index
    block : int | str
        Block index

    Returns
    -------
    bool
        True if it is point switch, False otherwise
        False if the block is not in the trajectory of
        one of the trains
    """
    if (
        block not in self.trajectory(train1)
        or
        block not in self.trajectory(train2)
    ):
        return False

    return (
        self.previous_block(train1, block)
        !=
        self.previous_block(train2, block)
        )


def is_just_after_a_point_switch(
    self,
    train1: int,
    train2: int,
    block
) -> bool:
    """Given two trains, is the block just after a point switch ?

    Parameters
    ----------
    train1 : int
        first train index
    train2 : int
        second train index
    block : int | str
        Track section index

    Returns
    -------
    bool
        True if it is just after a point switch, False otherwise
        False if the block is not in the trajectory
        of one of the trains
    """
    if (
        block not in self.trajectory(train1)
        or
        block not in self.trajectory(train2)
    ):
        return False

    return (
        ~self.is_a_point_switch(train1, train2, block)
        and
        self.is_a_point_switch(
            train1,
            train2,
            self.previous_block(train1, block)
        )
    )


def first_in(
    self,
    train1: int,
    train2: int,
    block: int | str
) -> int:
    """Among two trains, which one first enters the block"""

    trains_enter_at = (
        self.starts.loc[block, [train1, train2]].astype(float)
    )

    trains = (
        trains_enter_at.index[trains_enter_at == trains_enter_at.min()]
        .to_list()
    )

    if len(trains) == 1:
        return trains[0]
    return trains
