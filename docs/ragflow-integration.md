# RAGFlow Integration Guide

This guide covers two parts:

1. how to deploy RAGFlow
2. how to connect RAGFlow to the Admin Console

If you already run RAGFlow successfully, you can skip the deployment section and go straight to the Admin Console setup.

## Part 1: Deploy RAGFlow

### Step 1: Confirm that MySQL and Redis are reachable

RAGFlow depends on MySQL and Redis. If you already deployed the Admin Console stack, you may be able to reuse the same services.

From the host machine, test whether MySQL and Redis are reachable:

```sh
telnet 127.0.0.1 3306

telnet 127.0.0.1 6379
```

If both ports are reachable, continue to Step 2.

If they are not reachable:

- if your MySQL installation is isolated by your own packaging or service setup, fix host access to `3306` first
- if you deployed MySQL and Redis through this project's `docker-compose_all.yml`, expose those ports explicitly

Example before:

```yaml
  xiaozhi-esp32-server-db:
    ...
    networks:
      - default
    expose:
      - "3306:3306"
  xiaozhi-esp32-server-redis:
    ...
    expose:
      - 6379
```

Example after:

```yaml
  xiaozhi-esp32-server-db:
    ...
    networks:
      - default
    ports:
      - "3306:3306"
  xiaozhi-esp32-server-redis:
    ...
    ports:
      - "6379:6379"
```

After updating the compose file, restart the services:

```sh
# Run this in the directory that contains docker-compose_all.yml
cd xiaozhi-server
docker compose -f docker-compose_all.yml down
docker compose -f docker-compose.yml up -d
```

Then test again:

```sh
telnet 127.0.0.1 3306

telnet 127.0.0.1 6379
```

### Step 2: Create the database and user

Once MySQL is reachable from the host, create the `rag_flow` database and user:

```sql
CREATE DATABASE IF NOT EXISTS rag_flow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'rag_flow'@'%' IDENTIFIED BY 'infini_rag_flow';
GRANT ALL PRIVILEGES ON rag_flow.* TO 'rag_flow'@'%';

FLUSH PRIVILEGES;
```

### Step 3: Download the RAGFlow project

Choose a working directory and clone RAGFlow. The original guide used `v0.22.0`:

```sh
git clone https://ghfast.top/https://github.com/infiniflow/ragflow.git
cd ragflow
git checkout v0.22.0
cd docker
```

Edit `ragflow/docker/docker-compose.yml` and remove the `depends_on` block from `ragflow-cpu` and `ragflow-gpu` so they no longer expect RAGFlow's bundled MySQL service.

Before:

```yaml
  ragflow-cpu:
    depends_on:
      mysql:
        condition: service_healthy
    profiles:
      - cpu
  ...
  ragflow-gpu:
    depends_on:
      mysql:
        condition: service_healthy
    profiles:
      - gpu
```

After:

```yaml
  ragflow-cpu:
    profiles:
      - cpu
  ...
  ragflow-gpu:
    profiles:
      - gpu
```

Then edit `ragflow/docker/docker-compose-base.yml` and remove the bundled `mysql` and `redis` services if you want RAGFlow to reuse the services from your Xiaozhi deployment.

Before:

```yaml
services:
  minio:
    image: quay.io/minio/minio:RELEASE.2025-06-13T11-33-47Z
    ...
  mysql:
    image: mysql:8.0
    ...
  redis:
    image: redis:6.2-alpine
    ...
```

After:

```yaml
services:
  minio:
    image: quay.io/minio/minio:RELEASE.2025-06-13T11-33-47Z
    ...
```

### Step 4: Update environment variables

Edit `ragflow/docker/.env` and update the database and Redis settings carefully.

Important: make sure `MYSQL_USER` exists. Missing this field is a common setup mistake.

```env
# Port settings
SVR_WEB_HTTP_PORT=8008
SVR_WEB_HTTPS_PORT=8009

# MySQL
MYSQL_HOST=host.docker.internal
MYSQL_PORT=3306
MYSQL_USER=rag_flow
MYSQL_PASSWORD=infini_rag_flow
MYSQL_DBNAME=rag_flow

# Redis
REDIS_HOST=host.docker.internal
REDIS_PORT=6379
REDIS_PASSWORD=
```

If your Redis instance does not require a password, also edit `ragflow/docker/service_conf.yaml.template`.

Before:

```yaml
redis:
  db: 1
  password: '${REDIS_PASSWORD:-infini_rag_flow}'
  host: '${REDIS_HOST:-redis}:6379'
```

After:

```yaml
redis:
  db: 1
  password: '${REDIS_PASSWORD:-}'
  host: '${REDIS_HOST:-redis}:6379'
```

### Step 5: Start RAGFlow

```sh
docker-compose -f docker-compose.yml up -d
```

To inspect logs:

```sh
docker logs -n 20 -f docker-ragflow-cpu-1
```

If the logs show no startup errors, RAGFlow should be running successfully.

### Step 6: Create an account

Open `http://127.0.0.1:8008`, choose `Sign Up`, and create an account.

If you want to disable public signups later, set:

```dotenv
REGISTER_ENABLED=0
```

Then restart the stack:

```sh
docker-compose -f docker-compose.yml down
docker-compose -f docker-compose.yml up -d
```

### Step 7: Configure models inside RAGFlow

Sign in to RAGFlow, open the user menu, and go to settings.

Then:

1. open `Model Providers`
2. add an `LLM` provider and enter its API key
3. add a `TEXT EMBEDDING` provider and enter its API key
4. refresh the page
5. choose default models for both LLM and embedding

Make sure your provider account has access to the models you select.

## Part 2: Connect RAGFlow to the Admin Console

### Step 1: Create an API key in RAGFlow

Open `http://127.0.0.1:8008` and sign in.

From the user menu:

1. open settings
2. choose `API`
3. open `API Key`
4. select `Create new Key`
5. copy the generated API key

You will need that key in the Admin Console.

### Step 2: Enable the knowledge base feature

Make sure your Admin Console version is `0.8.7` or newer, and sign in with a super administrator account.

Enable the knowledge base feature first:

1. open `Parameter Dictionary`
2. open `System Feature Configuration`
3. enable `Knowledge Base`
4. save the configuration

The knowledge base section should now appear in the navigation.

### Step 3: Configure the RAGFlow provider

In the Admin Console:

1. open `Model Configuration`
2. open the `Knowledge Base` section
3. find `RAG_RAGFlow`
4. choose `Edit`

Set:

- `Service Address`: the LAN-accessible RAGFlow URL, for example `http://192.168.1.100:8008`
- `API Key`: the key you created in RAGFlow

Save the configuration.

### Step 4: Create a knowledge base

Sign in to the Admin Console as a super administrator.

Then:

1. open `Knowledge Base`
2. choose `Add`
3. enter a meaningful name and description
4. save it

Use descriptive names and summaries so retrieval quality is better. For example, if the knowledge base is about company information, use a name such as `Company Overview` and a description that explains what the documents contain.

After saving:

1. open the knowledge base details page
2. choose `Add` to upload documents
3. select `Parse` after upload
4. inspect the parsed chunks
5. run `Retrieval Test` to validate recall quality

### Step 5: Attach the knowledge base to an agent

In the Admin Console:

1. open `Agent`
2. find the agent you want to configure
3. choose `Configure Role`
4. use `Edit Functions` near the intent configuration area
5. select the knowledge base you want to attach
6. save the change

At that point, the agent can use the RAGFlow-backed knowledge base during interactions.
