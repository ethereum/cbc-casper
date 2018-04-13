from casper.validator_set import ValidatorSet
from casper.abstract_view import AbstractView
from casper.plot_tool import PlotTool

def test_protocol_callable_valid_json(protocol_class):
    assert callable(protocol_class.parse_json)


def test_protocol_init(protocol_instantiated):
    assert isinstance(protocol_instantiated.global_validator_set, ValidatorSet)
    assert isinstance(protocol_instantiated.global_view, AbstractView)
    assert isinstance(protocol_instantiated.plot_tool, PlotTool)

    assert isinstance(protocol_instantiated.unexecuted, str)
    assert isinstance(protocol_instantiated.executed, str)
    assert protocol_instantiated.executed == ''

    assert protocol_instantiated.messages_per_round >= 0
    assert protocol_instantiated.messages_this_round == 0

    assert isinstance(protocol_instantiated.messages, dict)
    assert isinstance(protocol_instantiated.message_from_hash, dict)
    assert isinstance(protocol_instantiated.message_name_from_hash, dict)
    assert isinstance(protocol_instantiated.handlers, dict)

    assert callable(protocol_instantiated.handlers['M'])
    assert protocol_instantiated.handlers['M'] == protocol_instantiated.make_message
    assert callable(protocol_instantiated.handlers['S'])
    assert protocol_instantiated.handlers['S'] == protocol_instantiated.send_message
    assert callable(protocol_instantiated.handlers['SJ'])
    assert protocol_instantiated.handlers['SJ'] == protocol_instantiated.send_and_justify


def test_protocol_saves_executed(protocol_instantiated):
    print(protocol_instantiated.unexecuted)
    protocol_instantiated.execute("M-0-A")
    assert protocol_instantiated.executed == "M-0-A"
    assert protocol_instantiated.unexecuted == ''
