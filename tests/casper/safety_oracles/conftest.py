import pytest

from casper.safety_oracles.clique_oracle import CliqueOracle
from casper.safety_oracles.turan_oracle import TuranOracle
from casper.safety_oracles.adversary_oracle import AdversaryOracle

ORACLES = [CliqueOracle, TuranOracle, AdversaryOracle]

@pytest.fixture(params=ORACLES)
def oracle_class(request):
    return request.param
