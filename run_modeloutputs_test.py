from RandomJungle.Data.ModelOutputs import BinaryModelOutput, HostMultiModelOutput, FlowMultiModelOutput
from RandomJungle.Data.Labels import BinaryLabel, HostAttackLabel, FlowAttackLabel


def test_binary_named_classes():
    probs = [0.2, 0.8]
    classes = ["Benign", "Attack"]
    out = BinaryModelOutput.from_proba(probs, classes)
    print('binary_named:', out.label, out.confidence, out.attack_probability)
    assert out.label == BinaryLabel.Attack
    assert abs(out.confidence - 0.8) < 1e-6


def test_binary_numeric_classes():
    probs = [0.7, 0.3]
    classes = [0, 1]
    out = BinaryModelOutput.from_proba(probs, classes)
    print('binary_numeric:', out.label, out.confidence, out.attack_probability)
    assert out.label == BinaryLabel.Benign


def test_binary_no_classes():
    probs = [0.4, 0.6]
    out = BinaryModelOutput.from_proba(probs, None)
    print('binary_none:', out.label, out.confidence, out.attack_probability)
    assert out.label == BinaryLabel.Attack


def test_host_multi_numeric_classes():
    probs = [0.1, 0.6, 0.2, 0.1]
    classes = [0, 1, 2, 3]
    out = HostMultiModelOutput.from_proba(probs, classes)
    print('host_multi_numeric:', out.label, out.confidence)
    assert out.label == HostAttackLabel.UdpScan


def test_flow_multi_numeric_classes():
    probs = [0.9, 0.1]
    classes = [0, 1]
    out = FlowMultiModelOutput.from_proba(probs, classes)
    print('flow_multi_numeric:', out.label, out.confidence)
    assert out.label == FlowAttackLabel.TcpFlood


if __name__ == '__main__':
    test_binary_named_classes()
    test_binary_numeric_classes()
    test_binary_no_classes()
    test_host_multi_numeric_classes()
    test_flow_multi_numeric_classes()
    print('ALL TESTS PASSED')

