# ochess

**ochess** is a backend for a real-time chess website (WIP).

## Installation
### Requirements
Python 3.11, pdm, PostgreSQL, Node JS. 

### Setup development environment
Setting up:
```bash
# Clone the repository
git clone git@github.com:immanelg/ochess.git && cd ochess

# Create `.env`
cp example.env .env

# Install python dependencies 
pdm sync

# Run database migrations (via `alembic`)
pdm run migrate-db -m "init"
pdm run upgrade-db

# Install Node dependencies
npm install
```

Available commands:
```bash
# Build and watch UI changes
npm run watch

# Start development server (on 127.0.0.1:8000)
pdm run serve-dev

# Run backend tests
pdm run test

# Run formatting and linting
pdm run fmt
pdm run lint
```

## Features
- Create new games in lobby room
- Accept/cancel invites
- Make moves with server-side validation and game position evaluation.

## TODO
- Refactor (socket communication handling (and API), channels, errors, DB sessions, repositories, leaking abstractions, validation, etc.)
- CI/CD, Docker, etc.
- Websocket Authentication && lichess auth.
- More game events: offer draw, claim draw, rematch, threefold repetition etc.
- Pydantic -> msgspec (ws.send_bytes).
- Use Redis backend for pub/sub.
- Timeouts for invites.
- Clocks.
- ELO ratings.
- HTTP API.
- Daily games.
- Tournaments, puzzles, etc.
