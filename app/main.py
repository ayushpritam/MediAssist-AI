from flask import Flask, request, jsonify
from app.agents.coordinator import generate_response

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json(force=True)
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({"response": "Please enter a message."})

    response = generate_response(user_message)
    return jsonify({"response": response})

if __name__ == '__main__':
    print("🚀 MediAssist Backend running on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
