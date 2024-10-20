---
slug: /config
title: Configuration
---

## Environment variables

You can configure the service at runtime using various environment variables:

- `MANTIS__SERVER__HOST` -
  host to run the server on
  (default: `0.0.0.0`)
- `MANTIS__SERVER__PORT` -
  port to run the server on
  (default: `10800`)
- `MANTIS__SERVER__TRUSTED` -
  trusted IP addresses
  (default: `*`)
- `MANTIS__STORE__PATH` -
  path to the store file
  (default: `data/state.json`)
- `MANTIS__OPERATIONS__STREAM__TIMEOUT` -
  timeout for trying to reserve a stream
  (default: `PT1H`)
- `MANTIS__OPERATIONS__STREAM__WINDOW` -
  duration of the time window for searching for past records
  (default: `P60D`)
- `MANTIS__CLEANER__REFERENCE` -
  reference datetime for cleaning
  (default: `2000-01-01T00:00:00`)
- `MANTIS__CLEANER__INTERVAL` -
  interval between cleanings
  (default: `P1D`)
- `MANTIS__SYNCHRONIZER__REFERENCE` -
  reference datetime for synchronization
  (default: `2000-01-01T00:00:00`)
- `MANTIS__SYNCHRONIZER__INTERVAL` -
  interval between synchronizations
  (default: `PT1M`)
- `MANTIS__SYNCHRONIZER__SYNCHRONIZERS__STREAM__WINDOW` -
  duration of the time window for stream tasks
  (default: `P1D`)
- `MANTIS__BEAVER__HTTP__SCHEME` -
  scheme of the HTTP API of the beaver service
  (default: `http`)
- `MANTIS__BEAVER__HTTP__HOST` -
  host of the HTTP API of the beaver service
  (default: `localhost`)
- `MANTIS__BEAVER__HTTP__PORT` -
  port of the HTTP API of the beaver service
  (default: `10500`)
- `MANTIS__BEAVER__HTTP__PATH` -
  path of the HTTP API of the beaver service
  (default: ``)
- `MANTIS__GECKO__HTTP__SCHEME` -
  scheme of the HTTP API of the gecko service
  (default: `http`)
- `MANTIS__GECKO__HTTP__HOST` -
  host of the HTTP API of the gecko service
  (default: `localhost`)
- `MANTIS__GECKO__HTTP__PORT` -
  port of the HTTP API of the gecko service
  (default: `10700`)
- `MANTIS__GECKO__HTTP__PATH` -
  path of the HTTP API of the gecko service
  (default: ``)
- `MANTIS__NUMBAT__HTTP__SCHEME` -
  scheme of the HTTP API of the numbat service
  (default: `http`)
- `MANTIS__NUMBAT__HTTP__HOST` -
  host of the HTTP API of the numbat service
  (default: `localhost`)
- `MANTIS__NUMBAT__HTTP__PORT` -
  port of the HTTP API of the numbat service
  (default: `10600`)
- `MANTIS__NUMBAT__HTTP__PATH` -
  path of the HTTP API of the numbat service
  (default: ``)
- `MANTIS__OCTOPUS__HTTP__SCHEME` -
  scheme of the HTTP API of the octopus service
  (default: `http`)
- `MANTIS__OCTOPUS__HTTP__HOST` -
  host of the HTTP API of the octopus service
  (default: `localhost`)
- `MANTIS__OCTOPUS__HTTP__PORT` -
  port of the HTTP API of the octopus service
  (default: `10300`)
- `MANTIS__OCTOPUS__HTTP__PATH` -
  path of the HTTP API of the octopus service
  (default: ``)
- `MANTIS__OCTOPUS__SRT__HOST` -
  host of the SRT stream of the octopus service
  (default: `localhost`)
- `MANTIS__OCTOPUS__SRT__PORT` -
  port of the SRT stream of the octopus service
  (default: `10300`)
- `MANTIS__DEBUG` -
  enable debug mode
  (default: `false`)
