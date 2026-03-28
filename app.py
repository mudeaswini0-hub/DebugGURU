from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import json

app = Flask(__name__)
CORS(app)

# ----------------- OpenAI Client -----------------
# Make sure you run this in CMD/PowerShell before running the app:
# setx OPENAI_API_KEY "YOUR_KEY_HERE"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------- Mistaken Memory -----------------
def save_error(error):
    """Save or update error count in mistakes.json"""
    try:
        with open("mistakes.json", "r") as f:
            data = json.load(f)
    except:
        data = {"errors": {}}

    if error in data["errors"]:
        data["errors"][error] += 1
    else:
        data["errors"][error] = 1

    with open("mistakes.json", "w") as f:
        json.dump(data, f, indent=4)

# ----------------- Rule-Based Analyzer -----------------
def analyze_logic(code):
    """Basic rule-based checks"""
    lines = code.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()

        if "print(" in stripped and not stripped.endswith(")"):
            return build_response(
                "Syntax Error",
                i,
                "You forgot to close the bracket in print statement.",
                stripped + ")",
                "Every opening bracket must have a closing ')'"
            )

        if "if" in stripped and not stripped.endswith(":"):
            return build_response(
                "Syntax Error",
                i,
                "Missing ':' in if condition.",
                stripped + ":",
                "Python uses ':' to define code blocks"
            )

    # Fallback unknown error
    return {"error": "Unknown"}

# ----------------- Response Builder -----------------
def build_response(error, line, explanation, fixed_code, learning):
    return {
        "error": error,
        "line": line + 1,
        "explanation": explanation,
        "fix": "Apply the suggested correction",
        "fixed_code": fixed_code,
        "learning": learning,
        "hints": [
            "Check this line carefully",
            "Review syntax rules"
        ]
    }

# ----------------- AI Fallback Analyzer -----------------
def ai_debug(code):
    prompt = f"""
You are a debugging assistant.

Code:
{code}

Explain the error in this format:

Error:
Line:
Explanation:
Fix:
Suggested Code:
Learning Mode:
"""
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ----------------- Main Analyze Route -----------------
@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    code = data.get('code')

    # Step 1: Rule-based analyzer
    result = analyze_logic(code)

    # Save the error in mistake memory
    save_error(result["error"])

    # Step 2: If unknown, use AI
    if result["error"] != "Unknown":
        return jsonify(result)

    try:
        ai_result = ai_debug(code)
        return jsonify({
            "error": "AI Detected",
            "line": "-",
            "explanation": ai_result,
            "fix": "See AI suggestion",
            "fixed_code": code,
            "learning": "AI generated explanation"
        })
    except Exception as e:
        return jsonify({
            "error": "System Error",
            "line": "-",
            "explanation": str(e),
            "fix": "Check API key / internet / installation",
            "fixed_code": code,
            "learning": "System failed"
        })

# ----------------- Run App -----------------
if __name__ == '__main__':
    app.run(debug=True)