# ochess

**ochess** is a backend for a real-time chess website.

## Installation
### Requirements
Python >= `3.11`, pdm, PostgreSQL, NodeJS. 

### Setup development environment
```bash
# Clone the repository
git clone git@github.com:immanelg/ochess.git && cd ochess

# Create `.env`
cp .env.example .env

# Install python dependencies 
pdm sync

# Run database migrations (via `alembic`)
pdm run migrate -m "init"
pdm run upgrade

# Install JS dependencies
npm install

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
Create new games in lobby room, accept/cancel invites, make moves with server-side validation and game position evaluation.

## TODO
Redis.
Actual authentication.
Abandoned games.
Clocks.
More game events: offer draw, claim draw, rematch, etc.
