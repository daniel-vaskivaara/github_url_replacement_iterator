FROM python:3.9-alpine

COPY src/* /opt

ENTRYPOINT ["python3", "/opt/github_action_test.py"]