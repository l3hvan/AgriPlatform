import os
import sys

# THIS is the critical fix — adds the project root to Python's path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriplatform.settings')

application = get_wsgi_application()
app = application   