from flask import Flask, render_template
import platform
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def client_dashboard():
    system_info = {
        "hostname": platform.node(),
        "os": platform.system(),
        "last_checkin": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Active"
    }
    return render_template('client.html', info=system_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
