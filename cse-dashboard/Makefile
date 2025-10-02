.PHONY: dev backend frontend test lint seed up

VENV?=.venv
PYTHON=${VENV}/bin/python
PIP=${VENV}/bin/pip

setup: ${VENV}/bin/activate

${VENV}/bin/activate:
python3 -m venv ${VENV}
${PIP} install -U pip
${PIP} install -r requirements.txt

backend-dev:
uvicorn backend.app:app --reload --port 8000

frontend-dev:
cd frontend && npm install && npm run dev

dev:
$(MAKE) -j2 backend-dev frontend-dev

seed:
${PYTHON} -m backend.services.seeding

lint:
ruff check backend
black --check backend
mypy backend

test:
pytest backend/tests

up:
docker compose -f deploy/docker-compose.yml up --build
