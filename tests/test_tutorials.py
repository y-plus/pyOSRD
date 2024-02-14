import glob
import shutil
import os

import nbformat
import pytest
from nbconvert.preprocessors import ExecutePreprocessor

TUTORIALS_PATH = 'doc/tutorials'
tuto_notebooks = sorted(list(glob.glob(f'{TUTORIALS_PATH}/*.ipynb')))


@pytest.mark.parametrize("notebook", tuto_notebooks)
def test_notebook_exec(notebook):
    with open(notebook) as f:
        nb = nbformat.read(f, as_version=4)
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        try:
            assert ep.preprocess(
                nb,
                resources={'metadata': {'path': TUTORIALS_PATH}},
            ) is not None, f"Got empty notebook for {notebook}"
        except Exception:
            assert False, f"Failed executing {notebook}"

    for dir_to_clean in ['small_infra', 'station_capacity2', 'tmp']:
        shutil.rmtree(
            os.path.join(TUTORIALS_PATH, dir_to_clean),
            ignore_errors=True,
            )
    if os.path.exists(
        res := os.path.join(TUTORIALS_PATH, 'existing_simulation/results.json')
    ):
        os.remove(res)
