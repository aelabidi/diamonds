import os

import requests
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

API_HOST = os.environ.get(
    "API_HOST", "https://diamonds-861302064365.europe-west1.run.app"
).rstrip("/")
API_PREDICT_PATH = os.environ.get("API_PREDICT_PATH", "/predict_one")

CUT_OPTIONS = ["Ideal", "Premium", "Good", "Very Good", "Fair"]
COLOR_OPTIONS = ["E", "I", "J", "H", "F", "G", "D"]
CLARITY_OPTIONS = ["SI2", "SI1", "VS1", "VS2", "VVS2", "VVS1", "I1", "IF"]


@app.route("/")
def home():
    return redirect(url_for("predict"))


def predict_url() -> str:
    return f"{API_HOST}{API_PREDICT_PATH}"


def check_api_connection() -> tuple[bool, str]:
    try:
        response = requests.get(f"{API_HOST}/", timeout=4)
        return (response.ok, f"API reachable ({response.status_code})")
    except requests.RequestException:
        # Some deployments only expose the prediction endpoint.
        try:
            probe_payload = {
                "carat": 0.77,
                "cut": "Ideal",
                "color": "E",
                "clarity": "SI1",
                "depth": 61.7,
                "table": 56.0,
                "x": 5.64,
                "y": 5.67,
                "z": 3.47,
            }
            probe = requests.post(predict_url(), json=probe_payload, timeout=6)
            probe.raise_for_status()
            return (True, "API connectee")
        except requests.RequestException as exc:
            return (False, f"Connexion impossible: {exc}")


@app.route("/predict", methods=["GET", "POST"])
def predict():
    prediction = None
    error = None
    status_message = None
    form_data = {}
    api_ok = None

    if request.method == "POST":
        form_data = request.form.to_dict()
        action = form_data.get("_action", "predict")

        if action == "check_api":
            api_ok, status_message = check_api_connection()
        else:
            try:
                payload = {
                    "carat": float(form_data.get("carat", 0.5)),
                    "cut": form_data.get("cut", "Ideal"),
                    "color": form_data.get("color", "E"),
                    "clarity": form_data.get("clarity", "SI1"),
                    "depth": float(form_data.get("depth", 61.0)),
                    "table": float(form_data.get("table", 55.0)),
                    "x": float(form_data.get("x", 0.0)),
                    "y": float(form_data.get("y", 0.0)),
                    "z": float(form_data.get("z", 0.0)),
                }
                response = requests.post(predict_url(), json=payload, timeout=10)
                response.raise_for_status()
                result = response.json()
                prediction = result.get("price")
                if prediction is None:
                    error = f"API response is missing 'price'. Response: {result}"
            except requests.exceptions.ConnectionError:
                error = "Prediction API is unreachable. Please make sure the API is running."
            except requests.exceptions.Timeout:
                error = "Prediction API timed out. Please try again."
            except requests.exceptions.HTTPError as exc:
                error = f"API returned an error: {exc}"
            except (ValueError, KeyError) as exc:
                error = f"Failed to parse API response: {exc}"

    return render_template(
        "predict.html",
        prediction=prediction,
        error=error,
        api_ok=api_ok,
        status_message=status_message,
        api_predict_url=predict_url(),
        form_data=form_data,
        cut_options=CUT_OPTIONS,
        color_options=COLOR_OPTIONS,
        clarity_options=CLARITY_OPTIONS,
    )


@app.route("/visualize")
def visualize():
    return render_template("visualize.html", api_host=API_HOST)


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=5000)
