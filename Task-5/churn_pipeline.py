import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold, cross_validate, GridSearchCV
from tabulate import tabulate
import joblib

def load_data():
    df = pd.read_csv(r"c:\Users\renua\Downloads\archive\data.csv")
    df = df.drop('customerID', axis=1)
    print(df.isnull().sum())
    df.info()
    print(df['PhoneService'].value_counts())
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'].replace(" ",np.nan))
    df['Churn'] = df['Churn'].map({'Yes':1,'No':0})
    return df

def feature_engineering(df):
    df = df.copy()
    df['avg_monthly_spend'] = df['TotalCharges'] / np.where(df['tenure'] == 0,1,df['tenure'])
    services = ['OnlineSecurity','OnlineBackup','DeviceProtection','TechSupport','StreamingTV','StreamingMovies']
    df['total_services'] = df[services].apply(lambda x: (x == 'Yes').sum(),axis=1)
    return df

def preprocess_data(X):
    num_cols = X.select_dtypes(include=['int64', 'float64']).columns
    cat_cols = X.select_dtypes(include=['object', 'category', 'string']).columns
    
    num_imputer = SimpleImputer(strategy='median')
    scaler = StandardScaler()
    X_num = num_imputer.fit_transform(X[num_cols])
    X_num_scaled = scaler.fit_transform(X_num)

    cat_imputer = SimpleImputer(strategy='most_frequent')
    X_cat = cat_imputer.fit_transform(X[cat_cols])
    ohe = OneHotEncoder(handle_unknown='ignore',drop='if_binary',sparse_output=False)
    X_cat_encoded = ohe.fit_transform(X_cat)

    X_processed = np.hstack((X_num_scaled, X_cat_encoded))

    cat_names = ohe.get_feature_names_out(cat_cols)
    all_names = list(num_cols) + list(cat_names)
    print(all_names)

    return X_processed, all_names


def get_models():
    return {
        'Random Forest': (
            RandomForestClassifier(random_state=42),
            {'max_depth':[5,10,None],'n_estimators':[100,200]}
        ),
        'Logistic Regression': (
            LogisticRegression(max_iter=1000,random_state=42),
            {'C':[0.01,0.1,1,10]}
        ),
        'SVM': (
            SVC(kernel='rbf',probability=True,random_state=42),
            {'C':[0.1,1,10],'gamma':['scale','auto']}
        ),
        'XGBoost': (
            XGBClassifier(eval_metric='logloss', random_state=42),
            {'max_depth':[3,5],'learning_rate':[0.05,0.1],'n_estimators':[100, 200]}
        ),
    }


def evaluate_models(models,X_processed,y):
    cv = StratifiedKFold(n_splits=5,shuffle=True,random_state=42)
    results = []

    for name,(model,_) in models.items():
        scores = cross_validate(model, X_processed , y , cv=cv , scoring=['accuracy','precision','recall','f1'])
        results.append([
            name,
            f"{scores['test_accuracy'].mean():.3f}",
            f"{scores['test_precision'].mean():.3f}",
            f"{scores['test_recall'].mean():.3f}",
            f"{scores['test_f1'].mean():.3f}"
        ])
        
    print(tabulate(results,headers=["Model","Accuracy","Precision","Recall","F1"],tablefmt="pretty"))
    best_model = max(results,key=lambda x: float(x[4]))[0]
    return best_model


def tune_model(best_name,models,X_processed,y):
    model,params = models[best_name]
    grid = GridSearchCV(model,params,cv=3,scoring='f1')
    grid.fit(X_processed,y)
    return grid.best_estimator_,grid.best_params_

def show_feature_importance(model, all_names):
    coefficients = model.coef_[0]
    df = pd.DataFrame({
        'Feature': all_names,
        'Coefficient': coefficients,
        'Importance': np.abs(coefficients)
    })
    df = df.sort_values(by='Importance', ascending=False).head(5)
    
    print(" TOP-5 FEATURE IMPORTANCES")
    for i,r in enumerate(df.itertuples(), 1):
        print(f"{i:2d}.{r.Feature:<35}|{r.Coefficient:.3f}")


def main():
    df = load_data()
    df = feature_engineering(df)
    X = df.drop('Churn', axis=1)
    y = df['Churn']
    X_processed,all_names = preprocess_data(X)
    models = get_models()

    best_name = evaluate_models(models,X_processed,y)
    print("\nBest Model:",best_name)

    best_model, best_params = tune_model(best_name,models,X_processed,y)
    print("Best Params:",best_params)

    show_feature_importance(best_model,all_names)

    joblib.dump(best_model,"telco_churn_model.pkl")
    print(f"\nSaved model to:telco_churn_model.pkl")

if __name__ == "__main__":
    main()