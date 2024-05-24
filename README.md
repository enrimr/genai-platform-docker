# Build image

```
docker build --pull --no-cache -t huggingface-model-app .
```


# Execute container

```
docker run -e MODEL_NAME=distilgpt2 -p 8000:8000 huggingface-model-app
```

With private model:

To use some models you should accept terms and conditions inside Hugging Face

````
docker run -e MODEL_NAME=meta-llama/Meta-Llama-3-8B -e HF_TOKEN=hf_token -p 8000:8000 -v ./../volume:/root/.cache/huggingface huggingface-model-app
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

# Cache models

Create a directory to host the cache

```
mkdir -p /path/to/your/cache
```

Execute the container with a volume

```
docker run -e MODEL_NAME=distilgpt2 -e HF_TOKEN=your_hf_token \
    -p 8000:8000 \
    -v /path/to/your/cache:/root/.cache/huggingface \
    huggingface-model-app
```
