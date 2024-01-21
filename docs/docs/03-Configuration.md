---
slug: /configuration
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
- `EMISCHEDULER__STREAM__TIMEOUT` -
  timeout for trying to reserve a stream
  (default: `PT1H`)
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
- `EMISCHEDULER__SYNCHRONIZER__WINDOW` -
  duration of the time window
  (default: `P1D`)
- `EMISCHEDULER__EMISHOWS__HOST` -
  host to connect to
  (default: `localhost`)
- `EMISCHEDULER__EMISHOWS__PORT` -
  port to connect to
  (default: `35000`)
- `EMISCHEDULER__EMIARCHIVE__HOST` -
  host to connect to
  (default: `localhost`)
- `EMISCHEDULER__EMIARCHIVE__PORT` -
  port to connect to
  (default: `30000`)
- `EMISCHEDULER__EMIARCHIVE__USER` -
  user to connect as
  (default: `readonly`)
- `EMISCHEDULER__EMIARCHIVE__PASSWORD` -
  password to connect with
  (default: `password`)
- `EMISCHEDULER__EMIARCHIVE__LIVE_BUCKET` -
  name of the bucket with recordings of live events
  (default: `live`)
- `EMISCHEDULER__EMIARCHIVE__PRERECORDED_BUCKET` -
  name of the bucket with prerecorded events
  (default: `prerecorded`)
- `EMISCHEDULER__EMISTREAM__HOST` -
  host to connect to
  (default: `localhost`)
- `EMISCHEDULER__EMISTREAM__PORT` -
  port to connect to
  (default: `10000`)
