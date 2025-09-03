## Steps to run

1. Fill in `.env`:
```shell
OPENAI_API_KEY=***
ENDPOINT_BEARER_TOKEN=***
ENDPOINT_URL=***
BUSINESSES_API_RETRIEVAL_URL=***
ELASTICSEARCH_URL=***
```

2. Start docker compose

```shell
docker compose up
```

3. Test the API
```shell
POST -F "file=@voice-to-text-test1.mp3" http://localhost:8080 | jq .
```