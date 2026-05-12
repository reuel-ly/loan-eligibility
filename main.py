import urllib.request
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Request data goes here
# The example below assumes JSON formatting which may be updated
# depending on the format your endpoint expects.
# More information can be found here:
# https://docs.microsoft.com/azure/machine-learning/how-to-deploy-advanced-entry-script
data = {
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

body = str.encode(json.dumps(data))

url = os.getenv("REST_ENDPOINT_URL")
# Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
api_key = os.getenv("API_KEY")
if not api_key:
    raise Exception("A key should be provided to invoke the endpoint")


headers = {'Content-Type':'application/json', 'Accept': 'application/json', 'Authorization':('Bearer '+ api_key)}

req = urllib.request.Request(url, body, headers)

try:
    response = urllib.request.urlopen(req)

    result = response.read()
    print(result)
except urllib.error.HTTPError as error:
    print("The request failed with status code: " + str(error.code))

    # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
    print(error.info())
    print(error.read().decode("utf8", 'ignore'))
