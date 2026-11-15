
from flask import Flask, request, jsonify, render_template

from jobs.main import match_jobs

app = Flask(__name__)


# Open website
@app.route("/")
def home():
    return render_template("index.html")


# Receive user details and match jobs
@app.route("/match", methods=["POST"])
def find_jobs():

    try:
        data = request.get_json()

        user_skills = data.get("skills", "")
        desired_role = data.get("role", "")

        results = match_jobs(user_skills, desired_role)

        return jsonify(results)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
