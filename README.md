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
| `sensor.den_tsa_east_standard` | East Security Standard lane wait time (min) |
| `sensor.den_tsa_east_precheck` | East Security PreCheck lane wait time (min) |
| `sensor.den_tsa_west_standard` | West Security Standard lane wait time (min) |
| `sensor.den_tsa_west_precheck` | West Security PreCheck lane wait time (min) |
| `sensor.den_tsa_south_standard` | South Standard lane wait time (min) |
| `sensor.den_tsa_south_precheck` | South PreCheck lane wait time (min) |

## Usage

Wait times are expressed as **midpoints** of ranges from the API (e.g. "0-4" → 2.0, "1-5" → 3.0), making them suitable for:

- History graphs
- Statistics cards
- Energy dashboard
- Lovelace gauge/history cards

Example Lovelace card:
```yaml
type: gauge
entity: sensor.den_tsa_east_standard
name: East Security Wait
min: 0
max: 30
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
