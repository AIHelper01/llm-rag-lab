<!-- derived-from: ../../02_%E7%BB%BC%E5%90%88%E5%AE%9E%E6%88%98/03_%E7%BB%BC%E5%90%88%E5%AE%9E%E6%88%98-RAGFlow.md -->
> English mirror, derived from the Chinese master: [the RAGFlow chapter](../../02_%E7%BB%BC%E5%90%88%E5%AE%9E%E6%88%98/03_%E7%BB%BC%E5%90%88%E5%AE%9E%E6%88%98-RAGFlow.md). The Chinese text is the source of truth; the screenshots are shared with it through `../../assets/`.

# Building a Knowledge Base on RAGFlow

## What is RAGFlow?

[RAGFlow](https://ragflow.io/) is a leading open-source retrieval-augmented generation (RAG) engine. It combines state-of-the-art RAG techniques with agent capabilities to give large language models an excellent context layer. It offers an end-to-end RAG workflow that adapts to companies of any size: a fused context engine plus ready-made agent templates let developers turn complex data into trustworthy, production-grade AI systems with real efficiency and precision.

## Try the demo

Sign in at [https://demo.ragflow.io](https://demo.ragflow.io/) to try the hosted demo.

## Key features

### "Quality in, quality out"
- Built on [deep document understanding](https://github.com/infiniflow/ragflow/blob/main/deepdoc/README.md), it extracts real insight from unstructured data in all kinds of awkward formats.
- It stays fast on needle-in-a-haystack retrieval even with effectively unlimited context (tokens).

### Template-based chunking
- Not just smart - controllable and explainable.
- A wide choice of text templates.

### Grounded answers, minimal hallucination
- The chunking process is visualised and can be adjusted by hand.
- Grounded: every answer shows snapshots of its key citations and lets you trace them back to the source.

### Works with heterogeneous data sources
- Many file types are supported: Word documents, PPT, spreadsheets, txt files, images, PDFs, scans, photocopies, structured data, web pages, and more.

### A fully automated, hands-off RAG workflow
- The optimised RAG workflow scales from personal apps up to very large enterprise ecosystems.
- Both the LLM and the embedding model are configurable.
- Multi-way recall with fused reranking.
- A convenient API makes it easy to embed into enterprise systems.

## System architecture
[![img](https://private-user-images.githubusercontent.com/33142505/501857358-31b0dd6f-ca4f-445a-9457-70cb44a381b2.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjM3MDQxOTYsIm5iZiI6MTc2MzcwMzg5NiwicGF0aCI6Ii8zMzE0MjUwNS81MDE4NTczNTgtMzFiMGRkNmYtY2E0Zi00NDVhLTk0NTctNzBjYjQ0YTM4MWIyLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTExMjElMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUxMTIxVDA1NDQ1NlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTk2NTMxNjNhMDgzYTM0NGI0NDAwZGJkMjQ3YmM3OTA4YmY5NWQzNDg2OTU2ZjQyYTY2YzRiZGFkOGYwOGNjM2QmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.EwVU0CLlrYC_fo3PbS-BxrIZUSu6CFD4T-L1_tzHd30)](https://private-user-images.githubusercontent.com/33142505/501857358-31b0dd6f-ca4f-445a-9457-70cb44a381b2.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjM3MDQxOTYsIm5iZiI6MTc2MzcwMzg5NiwicGF0aCI6Ii8zMzE0MjUwNS81MDE4NTczNTgtMzFiMGRkNmYtY2E0Zi00NDVhLTk0NTctNzBjYjQ0YTM4MWIyLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTExMjElMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUxMTIxVDA1NDQ1NlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTk2NTMxNjNhMDgzYTM0NGI0NDAwZGJkMjQ3YmM3OTA4YmY5NWQzNDg2OTU2ZjQyYTY2YzRiZGFkOGYwOGNjM2QmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.EwVU0CLlrYC_fo3PbS-BxrIZUSu6CFD4T-L1_tzHd30)

## Quick start

### Prerequisites

- CPU >= 4 cores
- RAM >= 16 GB
- Disk >= 50 GB
- Docker >= 24.0.0 & Docker Compose >= v2.26.1
- [gVisor](https://gvisor.dev/docs/user_guide/install/): only required if you plan to use RAGFlow's code executor (sandbox).

Tip:

If you do not have Docker installed yet (Windows, macOS or Linux), follow [Install Docker Engine](https://docs.docker.com/engine/install/).

### Start the server

#### Raise max_map_count

Make sure `vm.max_map_count` is at least 262144:

To check the current value of `vm.max_map_count`:
```
sysctl vm.max_map_count
```

If it is below 262144, reset it:
```
# set it to 262144 here:
$ sudo sysctl -w vm.max_map_count=262144
```

The change is lost on the next reboot. To make it permanent, also update `vm.max_map_count` in **/etc/sysctl.conf**:

```
vm.max_map_count=262144
```


#### Clone the repository

```bash
git clone https://bgithub.xyz/infiniflow/ragflow.git

```

#### Change the ports to avoid conflicts

**Option 1**: pass new ports when you run `docker compose` (recommended)
```
SVR_WEB_HTTP_PORT=8080 \
SVR_WEB_HTTPS_PORT=8443 \
MINIO_PORT=9100 \
MINIO_CONSOLE_PORT=9101 \
docker compose -f docker-compose.yml -p docker_ragflow up -d
```

**Option 2**: edit the variables in **docker/.env** before you run `docker compose`.
```bash
(base) root@server5:/opt/ragflow/docker# vim .env

change
SVR_WEB_HTTP_PORT=80
SVR_WEB_HTTPS_PORT=443
to
SVR_WEB_HTTP_PORT=8080
SVR_WEB_HTTPS_PORT=8443
```
If you already installed Milvus earlier in the course, ports 9000 and 9001 are taken as well, so change those too:

```bash
(base) root@server5:/opt/ragflow/docker# vim .env

change
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001
to
MINIO_PORT=9100
MINIO_CONSOLE_PORT=9101

```

#### Launch the services

Enter the **docker** folder and start the server from the prebuilt Docker images.

```bash
# enter RAGFlow's docker configuration directory
$ cd ragflow/docker

# switch to a stable release (recommended)
# optional: use a stable release tag (see https://github.com/infiniflow/ragflow/releases)
# this keeps the entrypoint.sh in the checkout aligned with the Docker image version.
$ git checkout v0.22.1

# option 1: run the DeepDoc service on CPU
$ SVR_WEB_HTTP_PORT=8080 \
SVR_WEB_HTTPS_PORT=8443 \
MINIO_PORT=9100 \
MINIO_CONSOLE_PORT=9101 \
docker compose -f docker-compose.yml up -d

# option 2: start under a custom project name (avoids container name conflicts) (recommended)
$ docker compose -f docker-compose.yml -p <your-project-name> up -d

# option 3: run the DeepDoc service on GPU (requires NVIDIA GPU support)
# add DEVICE=gpu as the first line of the .env file
$ sed -i '1i DEVICE=gpu' .env
$ docker compose -f docker-compose.yml up -d
```



In practice:

```bash
(base) root@server5:/opt#  cd ragflow/docker

(base) root@server5:/opt/ragflow/docker# docker compose -f docker-compose.yml -p docker_ragflow up -d
[+] Running 10/10
 ✔ Network docker_ragflow_ragflow          Created                                                                         0.1s
 ✔ Volume "docker_ragflow_redis_data"      Created                                                                         0.0s
 ✔ Volume "docker_ragflow_mysql_data"      Created                                                                         0.0s
 ✔ Volume "docker_ragflow_minio_data"      Created                                                                         0.0s
 ✔ Volume "docker_ragflow_esdata01"        Created                                                                         0.0s
 ✔ Container docker_ragflow-minio-1        Started                                                                         0.7s
 ✔ Container docker_ragflow-mysql-1        Healthy                                                                         21.3s
 ✔ Container docker_ragflow-redis-1        Started                                                                         0.8s
 ✔ Container docker_ragflow-es01-1         Started                                                                         0.9s
 ✔ Container docker_ragflow-ragflow-cpu-1  Started                                                                         21.8s
```





If a Docker image will not pull,

pull them one at a time:



```bash
(base) root@server5:/opt/ragflow/docker# docker compose -f docker-compose.yml pull mysql
...
```



You can also point `RAGFLOW_IMAGE` at a Huawei Cloud or Alibaba Cloud mirror, following the comments in **docker/.env**.

- Huawei Cloud image: `swr.cn-north-4.myhuaweicloud.com/infiniflow/ragflow`
- Alibaba Cloud image: `registry.cn-hangzhou.aliyuncs.com/infiniflow/ragflow`



Before:

```bash
# The RAGFlow Docker image to download. v0.22+ doesn't include embedding models.
RAGFLOW_IMAGE=infiniflow/ragflow:v0.22.1

# If you cannot download the RAGFlow Docker image:
# RAGFLOW_IMAGE=swr.cn-north-4.myhuaweicloud.com/infiniflow/ragflow:v0.22.1
# RAGFLOW_IMAGE=registry.cn-hangzhou.aliyuncs.com/infiniflow/ragflow:v0.22.1

```

After:

```bash
# The RAGFlow Docker image to download. v0.22+ doesn't include embedding models.
# RAGFLOW_IMAGE=infiniflow/ragflow:v0.22.1

# If you cannot download the RAGFlow Docker image:
# RAGFLOW_IMAGE=swr.cn-north-4.myhuaweicloud.com/infiniflow/ragflow:v0.22.1
RAGFLOW_IMAGE=registry.cn-hangzhou.aliyuncs.com/infiniflow/ragflow:v0.22.1


```





#### Confirm the service status

Once the server has started, check its status again:

```
docker logs -f docker_ragflow-ragflow-cpu-1
```



*The banner below means the server came up successfully:*

```
     ____   ___    ______ ______ __
    / __ \ /   |  / ____// ____// /____  _      __
   / /_/ // /| | / / __ / /_   / // __ \| | /| / /
  / _, _// ___ |/ /_/ // __/  / // /_/ /| |/ |/ /
 /_/ |_|/_/  |_|\____//_/    /_/ \____/ |__/|__/

 * Running on all addresses (0.0.0.0)
```



> If you try to sign in to RAGFlow before this banner appears, your browser may report `network anormal`.







### Sign in to RAGFlow

Open your server's IP address in a browser and sign in to RAGFlow.

`http://<IP>:8080` is enough; if you never changed the configuration, omit the port (the default HTTP port is 80).

Sign-up details - use any email and password you like for this local instance:

```
Email:
you@example.com
Password:
Choose-a-strong-password
```





![image-20251121155100750](../../assets/ragflow-01.png)



### Stop the services

Stop:

```
docker compose  -p docker_ragflow stop
```



Start:

```
docker compose  -p docker_ragflow start
```





Restart:

```
docker compose  -p docker_ragflow restart
```





### Uninstall RAGFlow



```
docker compose -p docker_ragflow down
```









## Using RAGFlow

Reference: https://ragflow.com.cn/docs/dev/



### Model providers

#### Model categories



![image-20251121160528051](../../assets/ragflow-02.png)

| Model type    | Full name / meaning                                      | What it is for                                                          |
| ------------- | -------------------------------------------------------- | ----------------------------------------------------------------------- |
| **LLM**       | **Large Language Model**                                  | The core of the application: it understands and generates human language - conversation, answers, writing, translation, coding. The default LLM is the application's main "brain". |
| **Embedding** | **Embedding model**                                       | Turns text (words, sentences, documents) into vectors of numbers that carry its deeper meaning. Used for knowledge-base retrieval, semantic search, classification and clustering - the basis of text similarity in AI. |
| **VLM**       | **Vision-Language Model**                                 | Handles images and text together: it can read picture content, answer visual questions, caption images, and hold image-grounded conversations. |
| **ASR**       | **Automatic Speech Recognition**                          | Converts human speech into text. The underlying technology behind voice input, live captions and voice assistants. |
| **Rerank**    | **Rerank model**                                          | In RAG and similar settings, once many relevant chunks are retrieved this model orders them precisely so the best few come first, materially improving answer accuracy and quality. |
| **TTS**       | **Text-to-Speech**                                        | Turns text into lifelike speech, giving applications voice interaction - audiobooks, voice assistants, announcement systems. |



#### Provider settings - Xinference

The models prepared during the model-deployment step are listed below.

|            |          | LLM                      | Embedding             | Reranker               |
| ---------- | -------- | ------------------------ | --------------------- | ---------------------- |
| xinference | base_url | http://localhost:9997/v1 | http://localhost:9997 | http://localhost:9997  |
|            | api_key  | NA                       | NA                    | NA                     |
|            | model    | my_qwen3_14b             | my_qwen3_embed_0.6b   | my_qwen3_reranker_0.6b |

Follow the steps below.

![image-20251121163051011](../../assets/ragflow-06.png)



![image-20251121163524365](../../assets/ragflow-07.png)



![image-20251121163749210](../../assets/ragflow-08.png)



![image-20251121163842565](../../assets/ragflow-09.png)





![image-20251121163908661](../../assets/ragflow-10.png)



#### Provider settings - vLLM

The models prepared during the model-deployment step are listed below.

|      |          | LLM                      | Embedding                | Reranker                 |
| ---- | -------- | ------------------------ | ------------------------ | ------------------------ |
| vLLM | base_url | http://localhost:9992/v1 | http://localhost:8000/v1 | http://localhost:8001/v1 |
|      | api_key  | your-vllm-token          | NA                       | NA                       |
|      | model    | my_qwen3_14b             | Qwen3-Embedding-0.6B     | Qwen3-Reranker-0.6B      |



![image-20251121164438201](../../assets/ragflow-11.png)



![image-20251121164607981](../../assets/ragflow-12.png)



#### Provider settings - Ollama

The models prepared during the model-deployment step are listed below.

<!-- previous embedding configuration:
base_url: http://localhost:11434
model: dengcao/Qwen3-Embedding-0.6B:F16
previous reranker configuration:
model: dengcao/Qwen3-Reranker-0.6B:F16
-->



|        |          | LLM                        | Embedding                        | Reranker                        |
| ------ | -------- | -------------------------- | -------------------------------- | ------------------------------- |
| Ollama | base_url | http://localhost:11434/v1/ | http://<your-ollama-host-ip>:11434 | http://localhost:11434          |
|        | api_key  | NA                         | NA                               | NA                              |
|        | model    | qwen3:8B                   | qwen3-embedding:0.6b             | dengcao/Qwen3-Reranker-0.6B:Q8_0 |







#### Provider settings - SiliconFlow

The models prepared during the model-deployment step are listed below.

|             |          | LLM                                            | Embedding                                 | Reranker                                  |
| ----------- | -------- | ---------------------------------------------- | ----------------------------------------- | ----------------------------------------- |
| siliconflow | base_url | https://api.siliconflow.cn/v1/chat/completions | https://api.siliconflow.cn/v1/embeddings  | https://api.siliconflow.cn/v1/rerank      |
|             | api_key  | Bearer your-siliconflow-key                    | Bearer your-siliconflow-key               | Bearer your-siliconflow-key               |
|             | model    | Qwen/Qwen3-8B                                  | BAAI/bge-m3                               | BAAI/bge-reranker-v2-m3                   |

Follow the steps below.

![image-20251121160932814](../../assets/ragflow-03.png)



![image-20251121160957364](../../assets/ragflow-04.png)



![image-20251121161102429](../../assets/ragflow-05.png)





#### Set the default models

![image-20251121165147984](../../assets/ragflow-13.png)





### Create a knowledge base

Test data path: your local corpus directory, e.g. `~/Documents/NetMAXHelper`.



![image-20251121165230758](../../assets/ragflow-14.png)



![image-20251121165303207](../../assets/ragflow-15.png)



![image-20251121165339460](../../assets/ragflow-16.png)



![image-20251121165513908](../../assets/ragflow-17.png)





![image-20251121165529440](../../assets/ragflow-18.png)



![image-20251121165659526](../../assets/ragflow-19.png)

Knowledge graph - GraphRAG



RAGFlow offers two different ways of processing the documents in your dataset to improve downstream retrieval. Both exist to capture the deeper structure of long or complex documents.

- A **knowledge graph** is like drawing a "who-knows-whom" map: it focuses on facts and relationships.
- **RAPTOR** is like building a "chapter summary tree": it focuses on the hierarchy and thread of a document.

| Feature        | Core idea                                                      | How it works                                                 | Strengths and good fits                                      |
| :------------- | :------------------------------------------------------------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| **Knowledge graph** | Extract entities (people, places, organisations) and the relations between them from documents, building a semantic network. | The system scans every document, identifies the key concepts (entities), decides how they relate (relations), and produces a visual "knowledge map". | **Strength**: retrieval does not stop at keyword matches - relations enable inference and linked queries. **Good fits**: documents full of facts, events and objects (research reports, annual reports, news archives); questions of the form "what is the relation between entity A and entity B?". |
| **RAPTOR**     | Recursively cluster and summarise a document into a layered tree. | 1. **Split** the long document into small chunks. 2. **Cluster and summarise**: group semantically similar chunks and write a summary for each group. 3. **Recurse**: treat those summaries as new "documents" and repeat, producing a hierarchy from details down to themes. | **Strength**: grasps the whole document at several granularities at once without losing context, which is ideal for long complex material. **Good fits**: books, long reports, academic papers - when you need the macro thesis without dropping key details. |

![image-20251121165806430](../../assets/ragflow-20.png)



![image-20251121170337314](../../assets/ragflow-21.png)





### Create a chat



![image-20251121170439755](../../assets/ragflow-22.png)



![image-20251121171734675](../../assets/ragflow-23.png)



## Resolving the Redis conflict with Dify

When RAGFlow and Dify share one machine their Redis instances can collide. The simplest fix:

start RAGFlow with a project name: `-p docker_ragflow`

start Dify with a project name: `-p docker_dify`


## Running several RAGFlow instances on one server
Port conflicts have to be resolved.

```bash
SVR_WEB_HTTP_PORT=1180 \
SVR_WEB_HTTPS_PORT=11443 \
SVR_HTTP_PORT=19380 \
ADMIN_SVR_HTTP_PORT=19381 \
SVR_MCP_PORT=19382 \
MINIO_PORT=19000 \
MINIO_CONSOLE_PORT=19001 \
ES_PORT=11200 \
MYSQL_PORT=15455 \
REDIS_PORT=16379 \
docker compose -f docker-compose.yml -p docker_ragflow1180 up -d

```

```bash
SVR_WEB_HTTP_PORT=2180 \
SVR_WEB_HTTPS_PORT=21443 \
SVR_HTTP_PORT=29380 \
ADMIN_SVR_HTTP_PORT=29381 \
SVR_MCP_PORT=29382 \
MINIO_PORT=29000 \
MINIO_CONSOLE_PORT=29001 \
ES_PORT=21200 \
MYSQL_PORT=25455 \
REDIS_PORT=26379 \
docker compose -f docker-compose.yml -p docker_ragflow2180 up -d

```

```bash
SVR_WEB_HTTP_PORT=3180 \
SVR_WEB_HTTPS_PORT=31443 \
SVR_HTTP_PORT=39380 \
ADMIN_SVR_HTTP_PORT=39381 \
SVR_MCP_PORT=39382 \
MINIO_PORT=39000 \
MINIO_CONSOLE_PORT=39001 \
ES_PORT=31200 \
MYSQL_PORT=35455 \
REDIS_PORT=36379 \
docker compose -f docker-compose.yml -p docker_ragflow3180 up -d

```


```bash
SVR_WEB_HTTP_PORT=4180 \
SVR_WEB_HTTPS_PORT=41443 \
SVR_HTTP_PORT=49380 \
ADMIN_SVR_HTTP_PORT=49381 \
SVR_MCP_PORT=49382 \
MINIO_PORT=49000 \
MINIO_CONSOLE_PORT=49001 \
ES_PORT=41200 \
MYSQL_PORT=45455 \
REDIS_PORT=46379 \
docker compose -f docker-compose.yml -p docker_ragflow4180 up -d

```
