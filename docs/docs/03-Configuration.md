---
slug: /config
title: Configuration
---

## Environment variables

You can configure the app at runtime using various environment variables:

- `EMISCHEDULER__SERVER__HOST` -
  host to run the server on
  (default: `0.0.0.0`)
- `EMISCHEDULER__SERVER__PORT` -
  port to run the server on
  (default: `33000`)
- `EMISCHEDULER__SERVER__TRUSTED` -
  trusted IP addresses
  (default: `*`)
- `EMISCHEDULER__STORE__PATH` -
  path to the store file
  (default: `data/state.json`)
- `EMISCHEDULER__OPERATIONS__STREAM__TIMEOUT` -
  timeout for trying to reserve a stream
  (default: `PT1H`)
- `EMISCHEDULER__OPERATIONS__STREAM__WINDOW` -
  duration of the time window for searching for past records
  (default: `P60D`)
- `EMISCHEDULER__CLEANER__REFERENCE` -
  reference datetime for cleaning
  (default: `2000-01-01T00:00:00`)
- `EMISCHEDULER__CLEANER__INTERVAL` -
  interval between cleanings
  (default: `P1D`)
- `EMISCHEDULER__SYNCHRONIZER__REFERENCE` -
  reference datetime for synchronization
  (default: `2000-01-01T00:00:00`)
- `EMISCHEDULER__SYNCHRONIZER__INTERVAL` -
  interval between synchronizations
  (default: `PT1M`)
- `EMISCHEDULER__SYNCHRONIZER__SYNCHRONIZERS__STREAM__WINDOW` -
  duration of the time window for stream tasks
  (default: `P1D`)
- `EMISCHEDULER__EMIRECORDS__HTTP__SCHEME` -
  scheme of the HTTP API of the emirecords service
  (default: `http`)
- `EMISCHEDULER__EMIRECORDS__HTTP__HOST` -
  host of the HTTP API of the emirecords service
  (default: `localhost`)
- `EMISCHEDULER__EMIRECORDS__HTTP__PORT` -
  port of the HTTP API of the emirecords service
  (default: `31000`)
- `EMISCHEDULER__EMIRECORDS__HTTP__PATH` -
  path of the HTTP API of the emirecords service
  (default: ``)
- `EMISCHEDULER__EMISHOWS__HTTP__SCHEME` -
  scheme of the HTTP API of the emishows service
  (default: `http`)
- `EMISCHEDULER__EMISHOWS__HTTP__HOST` -
  host of the HTTP API of the emishows service
  (default: `localhost`)
- `EMISCHEDULER__EMISHOWS__HTTP__PORT` -
  port of the HTTP API of the emishows service
  (default: `35000`)
- `EMISCHEDULER__EMISHOWS__HTTP__PATH` -
  path of the HTTP API of the emishows service
  (default: ``)
- `EMISCHEDULER__EMISTREAM__HTTP__SCHEME` -
  scheme of the HTTP API of the emistream service
  (default: `http`)
- `EMISCHEDULER__EMISTREAM__HTTP__HOST` -
  host of the HTTP API of the emistream service
  (default: `localhost`)
- `EMISCHEDULER__EMISTREAM__HTTP__PORT` -
  port of the HTTP API of the emistream service
  (default: `10000`)
- `EMISCHEDULER__EMISTREAM__HTTP__PATH` -
  path of the HTTP API of the emistream service
  (default: ``)
- `EMISCHEDULER__EMISTREAM__SRT__HOST` -
  host of the SRT stream of the emistream service
  (default: `localhost`)
- `EMISCHEDULER__EMISTREAM__SRT__PORT` -
  port of the SRT stream of the emistream service
  (default: `10000`)
- `EMISCHEDULER__DEBUG` -
  enable debug mode
  (default: `false`)
