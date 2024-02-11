import os
from rlway.osrd import _read_json


def test_read_json_bad_format():
    with open('bad.json', 'w') as file:
        file.write("{'a' 'b'}")
    assert _read_json('bad.json') == {}
    os.remove('bad.json')
