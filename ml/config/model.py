from lightgbm import LGBMClassifier

def set_model():
    return LGBMClassifier(
        n_estimators=200,
        learning_rate=0.05,
        num_leaves=7,
        min_data_in_leaf=15,
        min_data_in_bin=1,
        class_weight={0:1, 1:3},
        random_state=42
    )