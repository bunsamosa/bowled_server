# Bowled Server
Backend server for [Bowled.gg](https://bowled.gg/)

## Folder Structure
- `.vscode`
    - [`launch.json`](/.vscode/launch.json): VSCode debug configuration
    - [`settings.json`](/.vscode/settings.json): VSCode Formatting settings
- `/app`
    - [`main.py`](/app/main.py): FastAPI application entrypoint
    - [`import_routes.py`](/app/import_routes.py): HTTP Endpoint routers
    - [`middleware.py`](/app/middleware.py): Middleware hooks (ex: Logging)
- `/db_scrips`
    - [`create_tables.sql`](/db_scripts/create_tables.sql): SQL script to create tables
    - [`insert_sample_data.sql`](/db_scripts/insert_sample_data.sql): SQL script to insert sample data
- `/deployment`
    - [`nginx`](/deployment/nginx): Nginx configuration and dockerfile
    - [`rest_server`](/deployment/rest_server): REST server dockerfile
    - [`volumes`](/deployment/volumes): Directory for persistent data
- [`/dev`](/dev): Dev scripts dustbin
- `/gamelib`
    - [`cache_manager`](/gamelib/cache_manager): Cache manager
    - [`player`](/gamelib/player): Player related functions
    - [`team`](/gamelib/team): Team related functions
    - [`data_models`](/gamelib/data_models): Data models for the game
- `/lib`
    - `core`: Core libraries for rest server
        - [`auth_bearer`](/lib/core/auth_bearer.py): Authentication handler
        - [`cache_store`](/lib/core/cache_store.py): Redis connector
        - [`data_store`](/lib/core/data_store.py): Postgres connector
        - [`logger`](/lib/core/logger.py): Logging handler
    - [`utils`](/lib/utils): Utility functions
- [`/logs`](/logs): Directory to store persistent logs
- [`/rest_server`](/rest_server): HTTP endpoint handlers
- [`.pre-commit-config.yaml`](/.pre-commit-config.yaml): Pre-commit configuration
- [`docker-compose.yml`](/docker-compose.yml): Docker compose configuration
- [`docker-local.yml`](/docker-local.yml): Docker compose configuration for local development
- [`doppler.yaml`](/doppler.yaml): Doppler configuration for secrets
- [`pyproject.toml`](/pyproject.toml): Python project configuration


## Local Development
- Install [Poetry](https://python-poetry.org/docs/#installation)
- Install [VSCode](https://code.visualstudio.com/download)
- Clone the repo `git clone https://github.com/bunsamosa/bowled_server.git`
- Change directory `cd bowled_server`
- Install project dependencies with poetry `poetry install`
- Install pre-commit hooks `pre-commit install`
- The project uses [Doppler](https://www.doppler.com/) for secrets management. However, you can use the environment variables listed below.
- Setup the following environment variables
    - `REDIS_HOST`: Redis connection URI
    - `JWT_ALGORITHM`: `HS256`
    - `JWT_SECRET`: Secret key for JWT
    - `JWT_AUDIENCE`: Depends on your JWT authentication provider
    - `POSTGRES_URL`: Postgres connection URI
    - `POSTGRES_SCHEMA`: Postgres schema name
- Hit `F5` to start the server (VS Code will automatically start the debugger)
- Visit [http://127.0.0.1:9009/docs](http://localhost:8000/docs) to view the API docs
- Setup tables and sample data using scripts in [`/db_scripts`](/db_scripts)
