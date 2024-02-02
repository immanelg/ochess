# ochess

**ochess** is a backend for a real-time chess website (WIP).

## Installation
### Requirements
- Python 3.11 and pdm.
- Docker.
- GNU Make (optional).
- Node JS (optional).

### Setup development environment

```bash
# clone the repo
git clone git@github.com:immanelg/ochess.git && cd ochess

# create .env
cp example.env .env

# start docker container
docker network create app_main
make build
make up
make db-upgrade
```

You should be able to see the demo website at http://127.0.0.1:16000/.

Optionally, do `pre-commit install`.

See [Makefile](Makefile) for other available commands.

## Features
- Create/cancel/accept/list games in the lobby.
- Connect to games and make moves, resign, claim draw. The server validates moves, evaluates game position, etc, and notifies clients.

## TODO
- Do more refactoring on the backend.
- Expire old invites after some time of user being offline.
- Show online count and spectator count. Also, chat messages?
- Third-party authentication.
- ELO ratings.
- Clocks.
- TV.
- More events: claim_draw (check claimability on each move and store it in the db; also check for more types of automatic draws), offer_draw, rematch (just make a new private game inside a match). 
- Use Redis backend for pub/sub.
- HTTP API.
- Daily games.
- Tournaments, puzzles, etc.
- Create Vue.js frontend.
