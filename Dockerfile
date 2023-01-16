FROM python:3.9-alpine

COPY src/github_action_test.py /opt

ENTRYPOINT ["python3"]
CMD ["/opt/github_action_test.py"]