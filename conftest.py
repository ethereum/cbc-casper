import pytest

from testing_language import TestLangCBC


def pytest_addoption(parser):
    parser.addoption("--report", action="store_true", default=False,
                     help="plot TestLangCBC tests")


def run_test_lang_with_reports(test_string, weights):
    TestLangCBC(test_string, weights, True).parse()


def run_test_lang_without_reports(test_string, weights):
    TestLangCBC(test_string, weights, False).parse()


@pytest.fixture
def test_lang_runner(request):
    if request.config.getoption("--report"):
        return run_test_lang_with_reports
    else:
        return run_test_lang_without_reports
