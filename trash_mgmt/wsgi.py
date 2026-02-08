"""WSGI entrypoint tuned for PythonAnywhere.

On PythonAnywhere, set the WSGI configuration to point to
`trash_mgmt.wsgi.application` and choose the virtualenv and python version.
"""
import os
from django.core.wsgi import get_wsgi_application

# Ensure WSGI points to the consolidated settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trash_mgmt.settings')

application = get_wsgi_application()
