# api/tasks.py
from celery import shared_task
import subprocess

@shared_task
def run_converter_script():
    subprocess.run(["python", "/root/projects/django/smartlogger_api/api/monitor/converter.py"])