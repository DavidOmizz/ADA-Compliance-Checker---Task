from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import check_document

app = Flask(__name__)
CORS(app)

@app.route("/api/check/", methods=["POST"])
def check_html():
    data = request.get_json()
    if not data or "html" not in data:
        return jsonify({"error": "Missing 'html' in request body"}), 400
    html = data["html"]
    issues = check_document(html)
    return jsonify({"issues": issues})

if __name__ == "__main__":
    app.run(debug=True, port=8000)
