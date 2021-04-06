# Payroll Application

## Setup Development Environment

### Run the dev environment with Docker.

1. Please refer [Docker Install Doc](https://docs.docker.com/install/) to install the docker

2. Run the docker image via the docker-compose.
   ```bash
   docker-compose up -d --build
   ```
3. Open browser <http://127.0.0.1:8000/swagger/>. Need to wait for the server is ready.
4. To see the docker logs to run the following command.
   ```bash
   docker logs payroll_web_1
   ```

### Run development server

1. On Ubuntu system, install the underlying linux packages before installing the python dependencies.
   ```bash
   sudo apt-get install build-essential libssl-dev libffi-dev python3-dev
   ```
2. Create a virtual environment

   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

3. Make virtual enviorment using pip
   ```bash
   pip install -r docker/requirements.txt
   ```
4. Run development server
   ```bash
   python3 manage.py migrate
   python3 manage.py runserver
   ```
5. Open browser <http://127.0.0.1:8000/swagger/>

### Development tools we are using

To install pre-commit

```bash
pre-commit install
```

1. [Pre-commit as Git Pre-commit hooks](https://pre-commit.com/)
2. [Black as Code Formatter](https://github.com/psf/black)
3. [Reorder Python Imports as Code formatter](https://github.com/asottile/reorder_python_imports)
4. [Flake8 as Linker](https://github.com/PyCQA/flake8)

### Useful make utility commands:

1. `make or make run` for creating team monitor docker container.
2. `make stop` for stopping the team monitor docker container
3. `make test` for running test inside the team monitor docker container
4. `make clean` for deleting the team monitor docker container
