// WebSocket connection for live updates
let ws = null;

function connectWebSocket() {
    ws = new WebSocket(`ws://${window.location.host}/ws`);
    
    ws.onmessage = function(event) {
        const status = JSON.parse(event.data);
        updateStatus(status);
    };
    
    ws.onclose = function() {
        // Try to reconnect in 5 seconds
        setTimeout(connectWebSocket, 5000);
    };
}

function updateStatus(status) {
    document.getElementById('position').textContent = status.current_position;
    document.getElementById('magazine').textContent = status.magazin_name || '-';
    document.getElementById('status').textContent = status.running ? t('status.running') : t('status.stopped');
    document.getElementById('totalCards').textContent = status.total_cards_processed;
    document.getElementById('currentRunCards').textContent = status.current_run_cards;
    
    // Format run time as MM:SS
    const minutes = Math.floor(status.current_run_time / 60);
    const seconds = Math.floor(status.current_run_time % 60);
    document.getElementById('currentRunTime').textContent = 
        `${minutes}:${seconds.toString().padStart(2, '0')}`;
    
    // Update button states
    const startBtn = document.querySelector('#startForm button[type="submit"]');
    const stopBtn = document.getElementById('stopBtn');
    const emergencyBtn = document.getElementById('emergencyBtn');
    
    if (status.running) {
        startBtn.disabled = true;
        stopBtn.disabled = false;
        emergencyBtn.disabled = false;
    } else {
        startBtn.disabled = false;
        stopBtn.disabled = true;
        emergencyBtn.disabled = true;
    }
}

// Form submission
document.getElementById('startForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const magazinName = document.getElementById('magazinName').value;
    
    try {
        const response = await fetch('/process/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                magazin_name: magazinName
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            alert(`${t('messages.startError')}: ${error.detail}`);
        }
    } catch (error) {
        alert(t('messages.startError') + ': ' + error);
    }
});

// Stop buttons
document.getElementById('stopBtn').addEventListener('click', async function() {
    try {
        await fetch('/process/stop', {
            method: 'POST',
            body: JSON.stringify({ emergency: false })
        });
    } catch (error) {
        alert(t('messages.stopError') + ': ' + error);
    }
});

document.getElementById('emergencyBtn').addEventListener('click', async function() {
    if (confirm(t('messages.confirmEmergency'))) {
        try {
            await fetch('/process/stop', {
                method: 'POST',
                body: JSON.stringify({ emergency: true })
            });
        } catch (error) {
            alert(t('messages.emergencyError') + ': ' + error);
        }
    }
});

// Export button
document.getElementById('exportBtn').addEventListener('click', async function() {
    try {
        const response = await fetch('/csv/export-all', { method: 'POST' });
        const result = await response.json();
        alert(`CSV exported to: ${result.csv_path}`);
    } catch (error) {
        alert('Failed to export CSV: ' + error);
    }
});

// Connect WebSocket on load
connectWebSocket();