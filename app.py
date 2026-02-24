import os
from flask import Flask, render_template, request, jsonify, session
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# The secret key to lock the memory bank
app.secret_key = "prymage_helpdesk_memory_key" 

secure_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=secure_key)

@app.route('/')
def home():
    # Clear the memory when the page is refreshed so we start with a clean slate
    session.pop('history', None) 
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_ai():
    user_message = request.json.get('message')
    
    # Create the memory bank if it doesn't exist yet
    if 'history' not in session:
        session['history'] = []
        
    # Add the client's new message to the memory
    session['history'].append(f"Client: {user_message}")
    
    # Keep only the last 6 interactions so we don't overload the system
    if len(session['history']) > 6:
        session['history'] = session['history'][-6:]
        
    # Compile the memory into a single readable script
    transcript = "\n".join(session['history'])
    
    prompt = f"""
    You are the official AI Technical Support Agent for Prymage Consultancy Limited. 
    Your job is to provide instant, accurate help for Accounting Software (Tally, Odoo), ERP setups (ERPNext), and general client IT support.
    
    STRICT RULES:
    1. Keep answers clear, step-by-step, and easy for a non-technical client to understand.
    2. Do NOT use markdown formatting (no asterisks or hash symbols). Output plain text with standard paragraph spacing.
    3. THE GUARDRAIL: If a user asks a question completely unrelated to business software, IT, accounting, or Prymage, politely refuse and state you are an exclusive ERP/IT support agent.
    
    Here is the recent conversation transcript:
    {transcript}
    
    Agent Response:
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        ai_reply = response.text
        
        # Save the AI's answer to the memory bank so it remembers it next time
        session['history'].append(f"Agent: {ai_reply}")
        session.modified = True
        
    except Exception as e:
        ai_reply = "System Error: Unable to connect to Prymage Support."

    return jsonify({"reply": ai_reply})

@app.route('/clear', methods=['POST'])
def clear_memory():
    # This wipes the short-term memory bank when the Reset button is clicked
    session.pop('history', None)
    return jsonify({"status": "cleared"})

if __name__ == '__main__':
    app.run(debug=True)