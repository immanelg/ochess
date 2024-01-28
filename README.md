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
- Create/cancel/accept/list games in the lobby.
- Connect to games and make moves, resign, claim draw. The server validates moves, evaluates game position, etc, and notifies clients.

## TODO
- Do more refactoring on the backend.
- CI/CD, Docker, etc.
- Expire old invites after some time of user being offline.
- Show online count and spectator count. Also, chat messages?
- Third-party authentication.
- ELO ratings.
- Clocks.
- More events: claim_draw (check claimability on each move and store it in the db; also check for more types of automatic draws), offer_draw, rematch (just make a new private game inside a match). 
- Use Redis backend for pub/sub.
- HTTP API.
- Daily games.
- Tournaments, puzzles, etc.
- Make front-end client not proof-of-concept, but a little bit better.

