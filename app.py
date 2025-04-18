from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route("/", methods=["GET", "POST"])
def index():
    if "chat_history" not in session:
        session["chat_history"] = []

    if request.method == "POST":
        user_input = request.form["user_input"]
        bot_response = generate_bot_response(user_input)

        # Append to chat history
        session["chat_history"].append({"user": user_input, "bot": bot_response})
        session.modified = True  # Important: tells Flask the session has changed

        return redirect(url_for("index"))

    return render_template("index.html", chat_history=session["chat_history"])

def generate_bot_response(user_input):
    # Placeholder logic for now
    return "This is a response from Konnekt."

if __name__ == "__main__":
    app.run(debug=True)
