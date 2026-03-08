import os
import joblib
from RandomJungle.Data.FeatureSets import (
    HostBinaryFeatures,
    FlowBinaryFeatures,
    HostMultiFeatures,
    FlowMultiFeatures,
)

MODEL_FILES = {
    'hostBin': ('../Train/hostBin.pkl', HostBinaryFeatures),
    'flowBin': ('../Train/flowBin.pkl', FlowBinaryFeatures),
    'hostMulti': ('../Train/hostMulti.pkl', HostMultiFeatures),
    'flowMulti': ('../Train/flowMulti.pkl', FlowMultiFeatures),
}


def describe_model(name, path, feature_cls):
    print('='*60)
    print('Model:', name)
    if not os.path.exists(path):
        print('  MISSING:', path)
        return
    m = joblib.load(path)
    try:
        classes = getattr(m, 'classes_', None)
        n_features = getattr(m, 'n_features_in_', None)
        print('  classes_:', classes)
        print('  n_features_in_:', n_features)
        expected = len(feature_cls.FEATURE_NAMES)
        print('  expected feature count (from FeatureSets):', expected)
        if n_features is not None and expected != n_features:
            print('  WARNING: model expects different number of features than current FeatureSets -> retrain required')
    except Exception as e:
        print('  Error inspecting model:', e)


if __name__ == '__main__':
    for name, (path, cls) in MODEL_FILES.items():
        describe_model(name, path, cls)
    print('\nDone')

