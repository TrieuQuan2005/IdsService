from RandomJungle.Data.FeatureSets import (
    HostBinaryFeatures,
    FlowBinaryFeatures,
    HostMultiFeatures,
    FlowMultiFeatures,
)


def check(cls):
    inst = cls(**{name: 0 for name in cls.FEATURE_NAMES})
    arr = inst.to_array()
    if len(cls.FEATURE_NAMES) != arr.shape[0]:
        raise AssertionError(f"Mismatch in {cls.__name__}: FEATURE_NAMES={len(cls.FEATURE_NAMES)} vs array_len={arr.shape[0]}")
    print(f"OK: {cls.__name__} -> {arr.shape[0]} features")


if __name__ == '__main__':
    check(HostBinaryFeatures)
    check(FlowBinaryFeatures)
    check(HostMultiFeatures)
    check(FlowMultiFeatures)

    print('All feature sets consistent')

