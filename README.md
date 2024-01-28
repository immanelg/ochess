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

# Create .env
cp example.env .env

# Install python dependencies 
pdm install -d

# Install pre-commit
pdm run pre-commit install 

# Upgrade postgres database to the latest alembic version
pdm run db-upgrade

# Install Node dependencies
npm install
```

Available commands:
```bash
# Start development server (on 127.0.0.1:8000)
pdm run serve-dev

# Run backend tests
pdm run test

# Generate new alembic migration
pdm run db-migration 

# Upgrade database to the latest revision
pdm run db-upgrade

# Rollback database 
pdm run db-downgrade

# Run ruff formatting and linting
pdm run fmt
pdm run lint
pdm run check

# Build JS bundle
npm run build

# Build bundle with automatic reloading
npm run watch

# Format JS code
npm run fmt
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
