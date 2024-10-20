---
slug: /usage
title: Usage
---

## Automated broadcasts

There is a synchronization process
that runs at a fixed interval (default: 1 minute)
and checks if the streaming tasks
that are scheduled to run in a given time window (default: 1 day)
match the expected ones.
If there is a mismatch,
extra tasks are cancelled
and missing tasks are scheduled.

Each streaming task is scheduled to run
at a given time before the start of the broadcast (default: 15 minutes).
The flow of the task is the following:

1. Start running at the scheduled time.
2. Fetch matching event and its instance from `emishows` service.
3. Download recording from `emirecords` service and store it locally.
4. Wait until 10 seconds before the planned start of the broadcast.
5. Reserve the stream in `emistream` service.
6. Wait until 1 second before the planned start of the broadcast.
7. Start streaming the recording to the reserved stream.
8. Finish after the whole recording has been streamed.

## Tasks API

You can view and manage tasks by sending requests to `/tasks` endpoint.
Below are some examples of how to use it with `curl`.

### List tasks

```sh
curl \
    --request GET \
    http://localhost:33000/tasks
```

### Get generic task details

```sh
curl \
    --request GET \
    http://localhost:33000/tasks/85478e12-fd0d-4de3-a26b-cd1ec7f94f2b
```

### Get details about a task with a specific status

```sh
curl \
    --request GET \
    http://localhost:33000/tasks/failed/85478e12-fd0d-4de3-a26b-cd1ec7f94f2b
```

### Schedule a task manually

```sh
curl \
    --request POST \
    --header "Content-Type: application/json" \
    --data '{
      "operation": {"type": "test", "parameters": {}},
      "condition": {"type": "now", "parameters": {}},
      "dependencies": {}
    }' \
    http://localhost:33000/tasks
```

### Cancel a task

```sh
curl \
    --request DELETE \
    http://localhost:33000/tasks/85478e12-fd0d-4de3-a26b-cd1ec7f94f2b
```

### Clean stale tasks

```sh
curl \
    --request POST \
    --header "Content-Type: application/json" \
    --data '{
      "strategy": {"type": "all", "parameters": {}}
    }' \
    http://localhost:33000/tasks/clean
```

## Ping

You can check the status of the service by sending
either a `GET` or `HEAD` request to the `/ping` endpoint.
The service should respond with a `204 No Content` status code.

For example, you can use `curl` to do that:

```sh
curl \
    --request HEAD \
    --head \
    http://localhost:33000/ping
```
