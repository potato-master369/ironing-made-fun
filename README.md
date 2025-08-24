# Ironing Made Fun
A second version of the original scratch project, now for http! Port is at port 5000. Figure out the nginx reverse proxy yourself, configurations not included here.

## 🚀 Features
- Main website content and images
- Gunicorn configs (please adjust for your number of needed workers)
- app.py

## 🛠️ Installation
```bash
# Clone the repo
git clone https://github.com/potato-master369/ironing-made-fun

cd ironing-made-fun

# Install dependencies
# For Arch Linux:
sudo pacman -S python-flask python-flask-login python-flask-sqlalchemy python-werkzeug
# For Debian:
sudo apt install python3-flask python3-flask-login python3-flask-sqlalchemy python3-werkzeug
# For Fedora:
sudo dnf install python3-flask python3-flask-login python3-flask-sqlalchemy python3-werkzeug
# Using pip (any distro, requires pip installed):
pip install Flask Flask-Login Flask-SQLAlchemy Werkzeug

# set up systemd service
sudo chmod 644 /etc/systemd/system/imf2.service
cp ./imf2.service /etc/systemd/system
sudo systemctl enable imf2

# Create db
flask shell
```

```Flask shell
from app import db
from app import app, db
with app.app_context():
    db.create_all()
exit()
```

```bash
# Start service
sudo systemctl start imf2
```
