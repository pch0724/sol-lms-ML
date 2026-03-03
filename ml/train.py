from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix
from ml.feature.hrd_feature_engineering import build_hrd_features
from ml.feature.non_hrd_feature_engineering import build_non_hrd_features
from ml.config.model import set_model
import pandas as pd
import joblib
# import seaborn as sns
# import matplotlib.pyplot as plt

def train_model():

    # df1 = build_hrd_features()
    # df2 = build_non_hrd_features()
    # df = pd.concat([df1,df2], ignore_index=True)

    df = build_hrd_features()

    X = df.drop(columns=["trnee_id", "dropout_label"])
    y = df["dropout_label"]

    # print("=== X describe ===")
    # print(X.describe())

    # print("=== X nunique ===")
    # print(X.nunique())

    # 1. 변동 없는 컬럼 제거
    X = X.loc[:, X.nunique() > 1]
    print("=== After removing constant columns ===")
    print(X.nunique())

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

    # 2. 교차검증 (진짜 점수)
    cv_scores = cross_val_score(
        model,
        X,
        y,
        cv=5,
        scoring="roc_auc"   
    )

    print("===== 5-Fold CV ROC-AUC =====")
    print(cv_scores)
    print("Mean CV AUC:", cv_scores.mean())

    # 확률값
    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= 0.4).astype(int)

    risk_levels = [risk_grade(p) for p in y_prob]

    # print("===== 확률분포 =====")
    # print(pd.Series(y_prob).sort_values())

    # print("===== ROC-AUC (Hold-out) =====")
    # print(roc_auc_score(y_test, y_prob))

    print("===== Classification Report =====")
    print(classification_report(y_test, y_pred))

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

    print("===== risk grade value counts =====")
    print(result_df["risk_grade"].value_counts())

    print("===== result data frame =====")
    print(result_df[["trnee_id", "dropout_prob", "risk_grade"]].head())

    cm = confusion_matrix(y_test, y_pred)
    print(cm)

    return model

    # sns.heatmap(cm, annot=True, fmt="d")
    # plt.xlabel("Predicted")
    # plt.ylabel("Actual")
    # plt.show()

def risk_grade(prob):
    if prob >= 0.8:
        return "HIGH"
    elif prob >= 0.5:
        return "MEDIUM"
    else:
        return "LOW"