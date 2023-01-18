FROM python:3.9-alpine

COPY src/github_action_test.py /github/workspace/

CMD ["python3 /github/workspace/github_action_test.py"]