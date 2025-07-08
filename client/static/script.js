document.addEventListener('DOMContentLoaded', function() {
    // Update status every 10 seconds
    setInterval(updateStatus, 10000);
    
    function updateStatus() {
        fetch('/status')
            .then(response => response.json())
            .then(data => {
                document.querySelector('.value.status').className = 
                    `value status-${data.status.toLowerCase()}`;
                document.querySelector('.value.status').textContent = data.status;
                document.querySelector('.value.last-checkin').textContent = data.last_checkin;
            });
    }
});
