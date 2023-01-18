FROM python:3.9-alpine

# COPY entrypoint.sh /entrypoint.sh
# ENTRYPOINT ["/entrypoint.sh"]

COPY src/github_action_test.py /github_action_test.py
ENTRYPOINT ["python3 /github_action_test.py"]