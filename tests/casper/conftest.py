import pytest

from state_languages.blockchain_test_lang import BlockchainTestLang
from state_languages.integer_test_lang import IntegerTestLang
from state_languages.binary_test_lang import BinaryTestLang

TEST_LANGS = [BlockchainTestLang, IntegerTestLang, BinaryTestLang]


@pytest.fixture(params=TEST_LANGS)
def test_lang_creator(request, report):
    def creator(weights):
        return request.param(weights, report)
    return creator
