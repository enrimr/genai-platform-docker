# Build image

```
docker build --pull --no-cache -t huggingface-model-app .
```


# Execute container

```
docker run -e MODEL_NAME=gpt2 -p 8000:8000 huggingface-model-app
```


# Call model

```
curl --location 'http://localhost:8000/generate' \
--header 'Content-Type: application/json' \
--data '{
           "prompt": "Once upon a time",
           "max_length": 150,
           "temperature": 0.7,
           "top_k": 50,
           "top_p": 0.9
         }'

```