from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import confusion_matrix
from ml.feature.hrd_feature_engineering import build_hrd_features
from ml.feature.non_hrd_feature_engineering import build_non_hrd_features
from ml.config.model import set_model
import pandas as pd


def train_model():

    # df1 = build_hrd_features()
    # df2 = build_non_hrd_features()
    # df = pd.concat([df1,df2], ignore_index=True)

    df = build_hrd_features()

    X = df.drop(columns=["trnee_id", "dropout_label"])
    y = df["dropout_label"]

    # 1. 변동 없는 컬럼 제거
    X = X.loc[:, X.nunique() > 1]

    # train / test 분리
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.3,
        random_state=42,
        stratify=y
    )

    model = set_model()

    model.fit(X_train, y_train)

    # 확률값
    y_prob = model.predict_proba(X_test)[:, 1]

    # 3. Feature Importance 출력
    importance = pd.Series(
        model.feature_importances_,
        index=X.columns
    ).sort_values(ascending=False)

    print("===== Feature Importance =====")
    print(importance.head(10))


    result_df = df.loc[X_test.index].copy()
    result_df["dropout_prob"] = y_prob
    result_df["risk_grade"] = result_df["dropout_prob"].apply(risk_grade)

    return {
        "model": model,
        "features": X.columns.tolist()
    }

def risk_grade(prob):
    if prob >= 0.8:
        return "HIGH"
    elif prob >= 0.5:
        return "MEDIUM"
    else:
        return "LOW"