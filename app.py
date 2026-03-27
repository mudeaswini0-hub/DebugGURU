from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

def analyze_logic(code):
    return {
        "error": "Syntax Error",
        "explanation": "You might have missed a colon or bracket.",
        "fix": "Check loops and conditions.",
        "hints": [
            "Look at the last line",
            "Check brackets"
        ]
    }

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    code = data.get('code')

    result = analyze_logic(code)

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)