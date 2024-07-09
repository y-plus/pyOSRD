from pyosrd.utils.lists_utils import missing_elements_to_fill_holes


def test_missing_elements_to_fill_holes():

    REF_LIST = ['A', 'B', 'C', 'D']
    assert missing_elements_to_fill_holes(['A', 'B', 'C'], REF_LIST) ==\
        []
    assert missing_elements_to_fill_holes(['A', 'Z', 'D'], REF_LIST) ==\
        ['Z']
    assert missing_elements_to_fill_holes(['A', 'C'], REF_LIST) ==\
        []
    assert missing_elements_to_fill_holes(['A', 'C', 'D', 'X'], REF_LIST) ==\
        []
    assert missing_elements_to_fill_holes(['A', 'Y', 'C', 'Z'], REF_LIST) ==\
        ['Y']
    assert missing_elements_to_fill_holes(['A', 'Y', 'Z', 'C'], REF_LIST) ==\
        ['Y', 'Z']
    assert missing_elements_to_fill_holes(['A', 'C', 'Z'], REF_LIST) ==\
        []
    assert missing_elements_to_fill_holes(['Z', 'A', 'B', 'C'], REF_LIST) ==\
        []
    assert missing_elements_to_fill_holes(['Z', 'A', 'C'], REF_LIST) ==\
        []
    assert missing_elements_to_fill_holes(['A', 'Z', 'B'], REF_LIST) ==\
        ['Z']
