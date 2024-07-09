def missing_elements_to_fill_holes(
    list_to_check: list,
    reference_list: list
) -> list:
    """Detect missing element in a reference to fill holes in a given list

    Parameters
    ----------
    list_to_check : list
       List of element with potential ones not in the reference list
    reference_list : list
        List of elements

    Returns
    -------
    list
        Elements from list_to_check that are not in the reference
        and that are between two elements also in reference list

    Examples
    --------
    >>> ref_list = ['A', 'B', 'C', 'D']
    >>> missing_elements_to_fill_holes(['A', 'B', 'C'], ref_list)
    []
    >>> missing_elements_to_fill_holes(['A', 'Z', 'D'], ref_list)
    ['Z']
    >>> missing_elements_to_fill_holes(['A', 'C'], ref_list)
    []
    >>> missing_elements_to_fill_holes(['A', 'C', 'D', 'X'], ref_list)
    []
    >>> missing_elements_to_fill_holes(['A', 'Y', 'C', 'Z'], ref_list)
    ['Y']
    >>> missing_elements_to_fill_holes(['A', 'Y', 'Z', 'C'], ref_list)
    ['Y', 'Z']
    >>> missing_elements_to_fill_holes(['A', 'C', 'Z'], ref_list)
    []
    >>> missing_elements_to_fill_holes(['Z', 'A', 'B', 'C'], ref_list)
    []
    >>> missing_elements_to_fill_holes(['Z', 'A', 'C'], ref_list)
    []
    >>> missing_elements_to_fill_holes(['A', 'Z', 'B'], ref_list)
    ['Z']
    """
    check = [1 if e in reference_list else e for e in list_to_check]
    missings = [
        e for i, e in enumerate(check)
        if e != 1 and 1 in check[:i] and 1 in check[i:]
    ]

    return missings
