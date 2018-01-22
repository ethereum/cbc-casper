import pytest

from casper.safety_oracles.clique_oracle import CliqueOracle
from casper.safety_oracles.turan_oracle import TuranOracle
from casper.safety_oracles.adversary_oracle import AdversaryOracle

from state_languages.blockchain_test_lang import BlockchainTestLang
from state_languages.integer_test_lang import IntegerTestLang
from state_languages.binary_test_lang import BinaryTestLang


ORACLES = [CliqueOracle, TuranOracle, AdversaryOracle]

TEST_LANGS = [BlockchainTestLang, IntegerTestLang, BinaryTestLang]


@pytest.fixture(params=ORACLES)
def oracle_class(request):
    return request.param

@pytest.fixture(params=TEST_LANGS)
def test_lang_creator(request, report):
    def creator(weights):
        return request.param(weights, report)
    return creator
