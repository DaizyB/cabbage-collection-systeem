Trash Management - PythonAnywhere Deployment Guide

Overview
--------
This project is a Django 4.2 application
Quickstart (PythonAnywhere)
----------------------------
how to set up
```bash
git clone https://github.com/DaizyB/cabbage-collection-systeem.git
python3.11 -m venv ~/.virtualenvs/trash-mgmt
source ~/.virtualenvs/trash-mgmt/bin/activate
pip install -r requirements.txt
```

3. In the Web tab create a new Web app: choose manual configuration → Django → Python 3.11.
4. Set the WSGI file to point to `trash_mgmt.wsgi.application` and select the virtualenv path.
5. Set environment variables in the Web UI (e.g., `DJ_SECRET_KEY`, `DJ_DEBUG=0`, `DJ_ALLOWED_HOSTS`).
6. Point Static files mapping: URL `/static/` -> `/home/yourusername/yourrepo/staticfiles` and `/media/` -> `/home/yourusername/yourrepo/media`.
7. Run migrations and collectstatic in a Bash console:

```bash
source ~/.virtualenvs/trash-mgmt/bin/activate
cd ~/yourrepo
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Scheduled Tasks
---------------
PythonAnywhere doesn't support background workers on the free tier. Use the "Tasks" UI to schedule management commands:

- `process_pickups` every 5 minutes or hourly
- `send_notifications` every 10 minutes

Media and Scaling
-----------------
- Media is stored locally in `media/` for the free tier. For scaling, enable S3 using `django-storages` (see `settings/prod.py` comments).

Security
--------
- Do not commit secrets. Use Web UI env vars.
- `prod.py` raises errors for missing critical env vars.
- Ensure `DJ_DEBUG=0` in production.

Troubleshooting
---------------
- If static files are 404: run `collectstatic` and check static mapping in Web UI.
- If migrations fail: ensure virtualenv and Django version match.

Development
-----------
- Run locally:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

TODOs
-----
- Wire real payment provider webhooks and signature validation.
- Add SMS provider integration for notifications.
- Integrate geocoding service for addresses.
