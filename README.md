# Denver Airport TSA Wait Times for Home Assistant

A Home Assistant custom integration that maintains a WebSocket connection to the FlyDenver API and exposes TSA wait times as sensors.

[![HACS Default](https://img.shields.io/badge/HACS-Default-orange.svg)](https://hacs.xyz/)

## Features

- **Real-time updates** via WebSocket (no polling, no rate limits)
- **6 sensors** covering East, West, and South checkpoints (Standard + PreCheck lanes)
- **Range-to-midpoint conversion** for numeric time-series plotting
- **Automatic reconnection** on WebSocket drops
- **Zero configuration** — just install and add

## Installation via HACS

1. **Add this repository to HACS**
   - HACS → HACS Repositories → + → Add URL
   - Paste: `https://github.com/ahornerr/den-tsa-ha`

2. **Download**
   - Click "Download" on the repository card

3. **Restart Home Assistant**

4. **Add integration**
   - Settings → Devices & services → Add integration → Denver Airport TSA Wait Times
   - Click "Submit" (no configuration needed)

## Sensors

| Entity | Description |
|--------|-------------|
| `sensor.den_tsa_east_standard_wait` | East Security Standard lane wait time (min) |
| `sensor.den_tsa_east_precheck_wait` | East Security PreCheck lane wait time (min) |
| `sensor.den_tsa_west_standard_wait` | West Security Standard lane wait time (min) |
| `sensor.den_tsa_west_precheck_wait` | West Security PreCheck lane wait time (min) |

Wait times are expressed as **midpoints** of ranges from the API (e.g. "0-4" → 2.0, "1-5" → 3.0), making them numeric and suitable for history graphs.

## Lovelace Dashboard

Add this card to your dashboard for a full view with gauges and a 12-hour trend graph:

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## ✈ DEN TSA Wait Times
      _Updated in real-time_
    style: |
      ha-card {
        background: none;
        border: none;
        box-shadow: none;
        padding-bottom: 0;
      }
  - type: grid
    columns: 2
    square: false
    cards:
      - type: gauge
        entity: sensor.den_tsa_east_standard_wait
        name: East · Standard
        min: 0
        max: 30
        needle: true
        severity:
          - color: green
            from: 0
            to: 9
          - color: yellow
            from: 9
            to: 19
          - color: red
            from: 19
            to: 30
      - type: gauge
        entity: sensor.den_tsa_east_precheck_wait
        name: East · PreCheck ✓
        min: 0
        max: 30
        needle: true
        severity:
          - color: green
            from: 0
            to: 4
          - color: yellow
            from: 4
            to: 9
          - color: red
            from: 9
            to: 30
      - type: gauge
        entity: sensor.den_tsa_west_standard_wait
        name: West · Standard
        min: 0
        max: 30
        needle: true
        severity:
          - color: green
            from: 0
            to: 9
          - color: yellow
            from: 9
            to: 19
          - color: red
            from: 19
            to: 30
      - type: gauge
        entity: sensor.den_tsa_west_precheck_wait
        name: West · PreCheck ✓
        min: 0
        max: 30
        needle: true
        severity:
          - color: green
            from: 0
            to: 4
          - color: yellow
            from: 4
            to: 9
          - color: red
            from: 9
            to: 30
  - type: history-graph
    title: Wait Time Trends
    hours_to_show: 12
    entities:
      - entity: sensor.den_tsa_east_standard_wait
        name: East Standard
      - entity: sensor.den_tsa_east_precheck_wait
        name: East PreCheck
      - entity: sensor.den_tsa_west_standard_wait
        name: West Standard
      - entity: sensor.den_tsa_west_precheck_wait
        name: West PreCheck
```

## How it works

1. Integration maintains a persistent WebSocket connection to FlyDenver
2. Joins the "wait-times" channel
3. Parses lane data and converts range strings (e.g., "1-5") to midpoint floats
4. Updates sensor states in real-time as wait times change
5. Automatically reconnects if connection drops

## Troubleshooting

**Sensors showing `unavailable`:**
- Check HA logs (`Settings → System → Logs`) for WebSocket errors
- Verify internet connectivity
- The FlyDenver API may be temporarily down

**No updates:**
- Wait times only update when they actually change on FlyDenver
- Check if the checkpoint is currently open

## License

MIT
