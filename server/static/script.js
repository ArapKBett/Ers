let currentSession = null;

document.addEventListener('DOMContentLoaded', function() {
    loadClients();
    document.getElementById('execute-btn').addEventListener('click', executeCommand);
    setInterval(loadClients, 5000);
});

function loadClients() {
    fetch('/api/clients')
        .then(response => response.json())
        .then(clients => {
            const clientList = document.getElementById('client-list');
            const clientSelect = document.getElementById('client-select');
            
            // Update client list
            clientList.innerHTML = clients.map(client => `
                <div class="client-card" data-session="${client.session_id}">
                    <h3>${client.hostname} (${client.os})</h3>
                    <p><strong>IP:</strong> ${client.ip}</p>
                    <p><strong>Last Seen:</strong> ${new Date(client.last_seen).toLocaleString()}</p>
                    <button class="view-details" data-session="${client.session_id}">View Details</button>
                </div>
            `).join('');
            
            // Update select dropdown
            clientSelect.innerHTML = '<option value="">Select a client</option>' + 
                clients.map(client => `
                    <option value="${client.session_id}">
                        ${client.hostname} (${client.ip})
                    </option>
                `).join('');
            
            // Add event listeners
            document.querySelectorAll('.view-details').forEach(btn => {
                btn.addEventListener('click', function() {
                    currentSession = this.dataset.session;
                    loadCommandHistory(currentSession);
                });
            });
        });
}

function executeCommand() {
    const sessionId = document.getElementById('client-select').value;
    const command = document.getElementById('command-input').value;
    
    if (!sessionId || !command) return;
    
    fetch(`/api/execute?session=${sessionId}&command=${encodeURIComponent(command)}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('command-output').textContent = data.output;
            loadCommandHistory(sessionId);
        });
}

function loadCommandHistory(sessionId) {
    if (!sessionId) return;
    
    fetch(`/api/commands/${sessionId}`)
        .then(response => response.json())
        .then(commands => {
            const historyDiv = document.getElementById('command-history');
            historyDiv.innerHTML = commands.map(cmd => `
                <div class="command-entry">
                    <div class="command-meta">
                        <span class="command-time">${new Date(cmd.timestamp).toLocaleString()}</span>
                    </div>
                    <div class="command-content">${cmd.command}</div>
                </div>
            `).join('');
        });
                                     }
