import os

import requests
from flask import Flask, render_template, request, url_for

app = Flask(__name__)

API_HOST = os.environ.get("API_HOST", "http://localhost:8888").rstrip("/")

CUT_OPTIONS = ["Ideal", "Premium", "Good", "Very Good", "Fair"]
COLOR_OPTIONS = ["E", "I", "J", "H", "F", "G", "D"]
CLARITY_OPTIONS = ["SI2", "SI1", "VS1", "VS2", "VVS2", "VVS1", "I1", "IF"]


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/predict", methods=["GET", "POST"])
def predict():
    prediction = None
    error = None
    form_data = {}

    if request.method == "POST":
        form_data = request.form.to_dict()
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
            response = requests.post(
                f"{API_HOST}/predict_one", json=payload, timeout=10
            )
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
