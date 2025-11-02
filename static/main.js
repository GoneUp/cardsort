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
    
    // Display status with proper translations
    let statusText = t('status.stopped') || 'Stopped';
    if (status.running) {
        statusText = t('status.running') || 'Running';
    }
    document.getElementById('status').textContent = statusText;
    
    // Show notification if present
    if (status.notification) {
        if (status.notification === 'run_finished') {
            showNotification(t('messages.runFinished') || 'Run Finished!', 'success');
        }
    }
    
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

// Show notification modal that requires acknowledgment
function showNotification(message, type = 'info') {
    // Create backdrop
    const backdrop = document.createElement('div');
    backdrop.style.position = 'fixed';
    backdrop.style.top = '0';
    backdrop.style.left = '0';
    backdrop.style.width = '100%';
    backdrop.style.height = '100%';
    backdrop.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
    backdrop.style.zIndex = '9998';
    
    // Create modal container
    const modal = document.createElement('div');
    modal.style.position = 'fixed';
    modal.style.top = '50%';
    modal.style.left = '50%';
    modal.style.transform = 'translate(-50%, -50%)';
    modal.style.zIndex = '9999';
    modal.style.backgroundColor = 'white';
    modal.style.borderRadius = '8px';
    modal.style.padding = '40px';
    modal.style.minWidth = '500px';
    modal.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
    modal.style.textAlign = 'center';
    
    // Create message content
    const content = document.createElement('div');
    content.style.marginBottom = '30px';
    content.style.fontSize = '18px';
    content.style.lineHeight = '1.6';
    content.innerHTML = message;
    
    // Create acknowledge button
    const button = document.createElement('button');
    button.className = 'btn btn-primary btn-lg';
    button.textContent = 'OK';
    button.style.minWidth = '120px';
    button.onclick = () => {
        modal.remove();
        backdrop.remove();
    };
    
    modal.appendChild(content);
    modal.appendChild(button);
    document.body.appendChild(backdrop);
    document.body.appendChild(modal);
    
    // Play notification sound
    playNotificationSound();
}

// Play a simple notification sound using Web Audio API
function playNotificationSound() {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        // Set sound parameters - a pleasant "ding" sound
        oscillator.frequency.value = 800; // Hz
        oscillator.type = 'sine';
        
        // Create volume envelope
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
    } catch (error) {
        console.log('Could not play notification sound:', error);
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