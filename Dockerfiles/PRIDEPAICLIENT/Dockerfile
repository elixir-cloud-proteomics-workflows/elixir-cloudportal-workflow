FROM python:3.5-slim

RUN pip install requests wget
COPY pride_api_client.py /usr/local/bin/pride_api_client
RUN chmod ugo+x /usr/local/bin/pride_api_client

ENTRYPOINT ["pride_api_client"]
CMD ["--help"]
