import pandas as pd


def stations(
    self,
):
    ops = pd.json_normalize(self.infra['operational_points'])
    stations = ops[ops['extensions.sncf.ch'].isin(['BV', '00'])]
    return stations['extensions.identifier.name'].sort_values().values.tolist()


def platforms(
    self,
    station: str,
):
    track_sections = pd.json_normalize(self.infra['track_sections'])
    op = pd.json_normalize(self.infra['operational_points'])

    if station not in op['extensions.identifier.name'].unique():
        print(
            f'{station} is not a valid station in the infra.'
            ' Did you mean any of these ?')
        print(
            op[
                op['extensions.identifier.name']
                .str.contains(
                    station.lower(),
                    case=False
                )
            ]['extensions.identifier.name'].unique()
        )

    op_station = op[
        op['extensions.identifier.name'] == station
    ]

    op_station_platforms = op_station[
        op_station['extensions.sncf.ch'].isin(['BV', '00'])
    ]

    if len(op_station_platforms) == 0:
        return {}

    df = (
        pd.json_normalize(op_station_platforms.iloc[0].parts)
        .merge(
            track_sections[
                [
                    'id',
                    'extensions.sncf.track_name',
                    'extensions.sncf.line_code'
                ]
            ],
            left_on='track',
            right_on='id'
        )
    )

    return {
        row['extensions.sncf.track_name']: {
            'track_section': row['track'],
            'offset': row['position'],
            'line_code': row['extensions.sncf.line_code'],
        }
        for _, row in df.iterrows()
    }


def platform_location(
    self,
    station: str,
    track_name: str,
) -> tuple[str, float]:

    platform = platforms(self, station)[track_name]
    return (platform['track_section'], platform['offset'])


def lines(
    self
) -> pd.DataFrame:

    line_names = [
        (t['extensions']['sncf']['line_name'])
        for t in self.infra['track_sections']
    ]
    line_codes = [
        (t['extensions']['sncf']['line_code'])
        for t in self.infra['track_sections']
    ]

    return pd.DataFrame({
        'name': line_names,
        'code': line_codes
    }).drop_duplicates().reset_index(drop=True)
