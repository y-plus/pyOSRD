from rlway.schedules import Schedule


def three_trains() -> Schedule:
    schedule = Schedule(6, 3)

    schedule.df.at[0, 0] = [0, 1]
    schedule.df.at[2, 0] = [1, 2]
    schedule.df.at[3, 0] = [2, 3]
    schedule.df.at[4, 0] = [3, 4]

    schedule.df.at[1, 1] = [1, 2]
    schedule.df.at[2, 1] = [2, 3]
    schedule.df.at[3, 1] = [3, 4]
    schedule.df.at[5, 1] = [4, 5]

    schedule.df.at[0, 2] = [2, 3]
    schedule.df.at[2, 2] = [3, 4]
    schedule.df.at[3, 2] = [4, 5]
    schedule.df.at[4, 2] = [5, 6]

    return schedule


def two_trains_first_faster() -> Schedule:

    schedule = Schedule(6, 2)

    schedule.df.at[0, 0] = [0, 1]
    schedule.df.at[2, 0] = [1, 2]
    schedule.df.at[3, 0] = [2, 3]
    schedule.df.at[4, 0] = [3, 5]

    schedule.df.at[1, 1] = [0, 2]
    schedule.df.at[2, 1] = [2, 4]
    schedule.df.at[3, 1] = [4, 6]
    schedule.df.at[5, 1] = [6, 7]

    return schedule


def two_trains_first_slower() -> Schedule:

    schedule = Schedule(6, 2)

    schedule.df.at[0, 0] = [0, 2]
    schedule.df.at[2, 0] = [2, 4]
    schedule.df.at[3, 0] = [4, 6]
    schedule.df.at[4, 0] = [6, 8]

    schedule.df.at[1, 1] = [0, 4]
    schedule.df.at[2, 1] = [4, 6]
    schedule.df.at[3, 1] = [6, 7]
    schedule.df.at[5, 1] = [7, 8]

    return schedule
