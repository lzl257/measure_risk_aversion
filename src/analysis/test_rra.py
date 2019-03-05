"""
cP=1.79, cQ=1.21 from Szpiro (1986)
"""
import json
import sys
import numpy as np
import pytest


from numpy.testing import assert_array_equal
from szpiro import szp
from src.model_code.reg_model import reg_testh
from bld.project_paths import project_paths_join as ppj

spec = json.load(open(ppj('IN_MODEL_SPECS', 'values_in_interest.json'), encoding='utf-8'))
initial_test = spec['initial_test']
h_test = spec['h_test']
level = spec['level']

@pytest.fixture
def setup_rra():
    """
    Load the arguments szp() needs.
    
    """
    out = {}
    out['testh_model'] = reg_testh
    out['data_name'] = 'szpiro_table'
    out['initial_test'] = initial_test
    out['h_test'] = h_test
    out['level'] = level
    
    return out


@pytest.fixture
def expected_rra():
    """
    Results from Szpiro (1986)
    
    """
    
    return np.array([1.79, 1.21])


def test_rra(setup_rra, expected_rra):
    """
    Model Results == Expected Results?
    
    """
    calc_c = szp(**setup_rra)[0].round(2)
    
    assert_array_equal(calc_c, expected_rra)
    

if __name__ == '__main__':
    
    status = pytest.main([sys.argv[0]])
    sys.exit(status)