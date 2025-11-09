from flask import Flask, render_template, request, session
from flask_session import Session
import google.generativeai as genai
import os

app = Flask(__name__)

# --- Secret Key & Session ---
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback-secret")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# --- Check if API key is loaded ---
print("Gemini key loaded:", bool(os.environ.get("GOOGLE_API_KEY")))

# --- Configure Gemini API ---
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# --- Generation Settings ---
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# --- Gemini Model ---
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    safety_settings=safety_settings
)

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    response = ""
    chat_history = session.get("history", [])

    if request.method == "POST":
        user_input = request.form.get("inputItem", "")
        if user_input.strip():
            try:
                # Start a new chat with current history
                convo = model.start_chat(history=chat_history)
                convo.send_message(user_input)
                response = convo.last.text if convo.last else "No response"

                # Debug prints to logs
                print("User said:", user_input)
                print("Gemini replied:", response)

                chat_history.append({"role": "User", "text": user_input})
                chat_history.append({"role": "Bot", "text": response})
                session["history"] = chat_history

            except Exception as e:
                response = f"Oops! Something went wrong: {str(e)}"
                print("Error:", e)

    return render_template("index.html", response=response, chat_history=chat_history)


@app.route("/new")
def new_chat():
    session["history"] = []
    return render_template("index.html", response="", chat_history=[])


@app.route("/ping")
def ping():
    return "pong"


# --- Run ---
if __name__ == "__main__":
    app.run(debug=True)
