# awesounds

Synthesized interaction sounds for AwesomeWM. Inspired by [cuelume](https://github.com/Danilaa1/cuelume).

No audio files. No dependencies. Every cue is generated live from mathematical waveforms and piped to `ffplay` via stdout.

## Install

```bash
cd ~/awesounds
uv sync
```

## Usage

### CLI

```bash
uv run awesound press
uv run awesound success
uv run awesound toggle
```

### From AwesomeWM

```lua
awful.spawn.with_shell("uv run --project ~/awesounds awesound press")
```

### As a library

```python
from awesounds import play

play("chime")
```

## Available cues

| Cue | Description | Duration |
|-----|-------------|----------|
| `press` | Short click/tap | 30ms |
| `release` | Softer release click | 20ms |
| `tick` | Very short tick | 10ms |
| `toggle` | Two-tone toggle | 80ms |
| `success` | Ascending chime | 180ms |
| `error` | Descending buzz | 220ms |
| `chime` | Bell-like tone with harmonics | 250ms |
| `sparkle` | High frequency shimmer | 120ms |
| `droplet` | Water drop frequency sweep | 120ms |
| `bloom` | Swelling tone | 350ms |
| `whisper` | Filtered noise burst | 100ms |
| `loading` | Rhythmic pulse | 240ms |
| `ready` | Ascending chirp | 80ms |
| `page` | Page turn swoosh | 100ms |

## AwesomeWM example

Add to your `rc.lua`:

```lua
local function play_sound(cue)
    awful.spawn.with_shell("uv run --project ~/awesounds awesound " .. cue)
end

globalkeys = gears.table.join(
    -- Play a sound on tag switch
    awful.key({ modkey }, "Right", function()
        play_sound("tick")
        awful.tag.viewnext()
    end),

    -- Success sound on spawn
    awful.key({ modkey }, "Return", function()
        play_sound("press")
        awful.spawn(terminal)
    end),

    -- Error sound on quit prompt
    awful.key({ modkey, "Shift" }, "q", function()
        play_sound("error")
        awesome.quit()
    end)
)
```

## How it works

Each cue is a pure function `fn(t) -> float` that returns a sample value at time `t`. The synth:

1. Evaluates the function at 44100 Hz
2. Converts to 16-bit PCM
3. Pipes raw bytes to `ffplay -f s16le -ar 44100 -ac 1 -i pipe:0`

Total code size: ~5 kB. No recordings, no runtime dependencies.

## License

MIT
