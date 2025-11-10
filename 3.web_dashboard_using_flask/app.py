import os, psutil, datetime, socket
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, render_template_string
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = '26e4c45477343cac8cc28328647035d86bda27a4a75f368a2d281679b370be53'

# Path to mounted USB folder
app.config['UPLOAD_FOLDER'] = '/mnt/usb128GB/share'

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

users = {'pi': generate_password_hash('1994')}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

def get_ip():
    """Return device IP dynamically."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and check_password_hash(users[username], password):
            login_user(User(username))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash(f'Uploaded {filename}')
        return redirect(url_for('dashboard'))

    try:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
    except FileNotFoundError:
        files = []

    rows = ""
    for file in files:
        rows += f"""
        <tr>
            <td>{file}</td>
            <td>
                <a href="{url_for('download_file', filename=file)}" class="btn btn-sm btn-success">Download</a>
                <a href="{url_for('delete_file', filename=file)}" class="btn btn-sm btn-danger" onclick="return confirm('Delete {file}?');">Delete</a>
            </td>
        </tr>
        """

    # compute free USB space
    usage = psutil.disk_usage(app.config['UPLOAD_FOLDER'])
    free_space = f"{usage.free / (1024**3):.2f} GB free of {usage.total / (1024**3):.2f} GB"
    monitor_url = f"http://{get_ip()}:5000/monitor"

    return render_template('dashboard.html', file_rows=rows, free_space=free_space, monitor_url=monitor_url)

@app.route('/download/<path:filename>')
@login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<path:filename>')
@login_required
def delete_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash(f'Deleted {filename}')
    else:
        flash(f'File {filename} not found')
    return redirect(url_for('dashboard'))

# ---------------------- MONITOR ROUTE ----------------------
def human_size(n):
    for unit in ['B','KB','MB','GB','TB']:
        if n < 1024.0:
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} PB"

def is_app_running(match_name="app.py"):
    for p in psutil.process_iter(['pid','name','cmdline']):
        try:
            cmd = " ".join(p.info.get('cmdline') or [])
            if match_name in cmd or match_name in (p.info.get('name') or ""):
                return True, p.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False, None

def list_dir_sizes(path):
    entries = []
    if not os.path.exists(path):
        return entries
    with os.scandir(path) as it:
        for e in it:
            try:
                size = e.stat().st_size if e.is_file() else sum(f.stat().st_size for f in os.scandir(e.path)) if e.is_dir() else 0
            except Exception:
                size = 0
            entries.append((e.name, human_size(size)))
    entries.sort()
    return entries

MONITOR_TEMPLATE = """
<!doctype html>
<html>
<head>
<meta http-equiv="refresh" content="10">
<title>NAS Monitor</title>
<style>
body { font-family: Arial; background: #fafafa; margin: 20px; }
table { border-collapse: collapse; width: 70%; }
th, td { border: 1px solid #888; padding: 6px; text-align: left; }
th { background: #ddd; }
</style>
</head>
<body>
<h3>NAS Monitor</h3>
<p>Status: <b style="color:{{'green' if running else 'red'}}">{{'Running' if running else 'Stopped'}}</b>
{% if pid %}(PID {{pid}}){% endif %}</p>
<p>Checked at {{ts}}</p>
<p><b>Free Space:</b> {{free_space}}</p>
<table>
<tr><th>Name</th><th>Size</th></tr>
{% for name, size in files %}
<tr><td>{{name}}</td><td>{{size}}</td></tr>
{% endfor %}
</table>
</body>
</html>
"""

@app.route("/monitor")
@login_required
def monitor():
    running, pid = is_app_running("app.py")
    files = list_dir_sizes(app.config['UPLOAD_FOLDER'])
    usage = psutil.disk_usage(app.config['UPLOAD_FOLDER'])
    free_space = f"{usage.free / (1024**3):.2f} GB free of {usage.total / (1024**3):.2f} GB"
    return render_template_string(MONITOR_TEMPLATE,
                                  running=running,
                                  pid=pid,
                                  ts=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                  files=files,
                                  free_space=free_space)
# ----------------------------------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
