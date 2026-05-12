# Loan Eligibility Classification

This repository contains a loan eligibility classification project. The model development work is in `loan_eligibility.ipynb`, and `main.py` is a small client script that calls a deployed Azure Machine Learning endpoint for inference.

## Codebase Structure

```text
loan-eligibility/
+-- main.py
+-- loan_eligibility.ipynb
+-- pyproject.toml
+-- uv.lock
+-- README.md
+-- LICENSE
`-- dataset/
    +-- loan-eligibility/
    |   +-- loan-train.csv
    |   `-- loan-test.csv
    `-- home-loan-eligibility/
        +-- loan_sanction_train.csv
        `-- loan_sanction_test.csv
```

## Main Components

### `main.py`

`main.py` sends a sample loan application request to an AzureML REST endpoint.

The script:

1. Loads environment variables from a `.env` file using `python-dotenv`.
2. Builds a JSON payload with one loan applicant record.
3. Reads the AzureML endpoint URL from `REST_ENDPOINT_URL`.
4. Reads the endpoint API key or token from `API_KEY`.
5. Sends the request using `urllib.request`.
6. Prints the endpoint response or prints AzureML error details if the request fails.

Required environment variables:

```env
REST_ENDPOINT_URL=https://your-azureml-endpoint-url
API_KEY=your_endpoint_key_or_token
```

The payload currently uses this input shape:

```json
{
  "Inputs": {
    "input1": [
      {
        "Loan_ID": "LP001002",
        "Gender": "Male",
        "Married": "No",
        "Dependents": "0",
        "Education": "Graduate",
        "Self_Employed": "No",
        "ApplicantIncome": 5849,
        "CoapplicantIncome": 0,
        "LoanAmount": 128,
        "Loan_Amount_Term": 360,
        "Credit_History": 1,
        "Property_Area": "Urban"
      }
    ]
  },
  "GlobalParameters": {}
}
```

This format should match the input contract of the deployed AzureML model.

### `loan_eligibility.ipynb`

`loan_eligibility.ipynb` contains the notebook workflow used as the basis for the AzureML classification model.

The notebook uses the `dataset/loan-eligibility` data and follows this general workflow:

1. Load the training data from `loan-train.csv`.
2. Drop the `Loan_ID` column for model training.
3. Fill missing categorical values with each column's mode.
4. Fill missing numeric values with each column's median.
5. Encode categorical columns.
6. Create engineered features:
   - `TotalIncome = ApplicantIncome + CoapplicantIncome`
   - `LoanAmountPerTerm = LoanAmount / (Loan_Amount_Term + 1)`
   - `DebtToIncome = LoanAmount / (TotalIncome + 1)`
7. Split the data into train and test sets with stratification.
8. Train an `XGBClassifier`.
9. Evaluate the model using classification metrics, ROC-AUC, and a confusion matrix.
10. Generate SHAP-based feature importance.
11. Predict loan eligibility for records in `loan-test.csv`.

The notebook target column is:

```text
Loan_Status
```

where the labels represent whether a loan is approved or rejected.

## Dataset

The project currently uses:

```text
dataset/loan-eligibility/
+-- loan-train.csv
`-- loan-test.csv
```

`loan-train.csv` contains 614 data rows plus a header row. It includes the training target column `Loan_Status`.

`loan-test.csv` contains 367 data rows plus a header row. It has the same applicant feature columns but does not include `Loan_Status`.

### Columns

| Column | Description |
| --- | --- |
| `Loan_ID` | Unique loan application identifier. Used for tracking records, not for training. |
| `Gender` | Applicant gender. |
| `Married` | Applicant marital status. |
| `Dependents` | Number of dependents. |
| `Education` | Applicant education level. |
| `Self_Employed` | Whether the applicant is self-employed. |
| `ApplicantIncome` | Applicant income. |
| `CoapplicantIncome` | Co-applicant income. |
| `LoanAmount` | Requested loan amount. |
| `Loan_Amount_Term` | Loan repayment term. |
| `Credit_History` | Credit history flag. |
| `Property_Area` | Property area category. |
| `Loan_Status` | Training target. Present only in training data. |

The repository also contains:

```text
dataset/home-loan-eligibility/
+-- loan_sanction_train.csv
`-- loan_sanction_test.csv
```

Those files appear to have the same loan eligibility schema, but the current model workflow is based on `dataset/loan-eligibility`.

## Setup

This project uses Python `>=3.13`.

Install dependencies:

```bash
uv sync
```

The committed project dependency is:

```text
python-dotenv
```

The notebook also uses additional data science packages, including:

```text
pandas
scikit-learn
xgboost
shap
matplotlib
```

Install those packages in the notebook or AzureML training environment if you need to rerun model development.

## Running AzureML Inference

Create a `.env` file in the project root:

```env
REST_ENDPOINT_URL=https://your-azureml-endpoint-url
API_KEY=your_endpoint_key_or_token
```

Run the endpoint client:

```bash
uv run python main.py
```

Expected behavior:

- On success, the script prints the AzureML endpoint response.
- On failure, the script prints the HTTP status code, response headers, and response body to help debug the AzureML request.

## AzureML Endpoint Notes

The deployed AzureML model must expect the same feature names and compatible data types as the request in `main.py`.

Important alignment points:

- The notebook drops `Loan_ID` for local training, but `main.py` includes `Loan_ID` in the AzureML request payload. The deployed AzureML scoring pipeline must either ignore `Loan_ID` or handle it consistently.
- The notebook creates engineered features during local modeling. If the deployed endpoint expects raw applicant fields, feature engineering must be included in the AzureML scoring pipeline. If the endpoint expects engineered features, `main.py` must send them.
- Categorical values such as `Gender`, `Married`, `Education`, `Self_Employed`, `Dependents`, and `Property_Area` must be transformed the same way during training and inference.


