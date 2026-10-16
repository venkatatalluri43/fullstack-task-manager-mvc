# Full-Stack Task Manager (MVC + Docker + CI/CD + K8s simulation)

A multi-user CRUD task manager built to simulate a production-like deployment
on a developer laptop: REST API backend, SPA frontend, containerization,
local CI/CD, and optional Kubernetes/Nginx infrastructure simulation.

## Stack

| Layer      | Choice                                   |
|------------|-------------------------------------------|
| Backend    | Python + Flask (REST API, JWT auth)        |
| Frontend   | React (Vite)                               |
| Database   | SQLite                                     |
| Container  | Docker, docker-compose                     |
| CI/CD      | GitHub Actions                             |
| Infra sim  | Nginx reverse proxy, Kubernetes (Minikube/Kind) manifests |

## Architecture (MVC)

```
backend/
  app/
    models/        # Data schema & DB access (SQLAlchemy) — User, Project, Task
    views/         # HTTP routing layer (Flask blueprints) — request/response only
    controllers/    # Business logic — auth rules, project/task ownership, assignment, validation
  config.py         # Flask config (SQLite path, JWT secret/expiry)
  run.py / wsgi.py   # Entrypoints (dev server / gunicorn)
  tests/             # pytest suite (30 tests — auth, projects, tasks, users)

frontend/
  src/
    pages/           # Route-level screens — Dashboard, Projects, ProjectDetail, MyWork, Profile, Login
    layouts/          # AppLayout — sidebar + routed content shell
    components/       # Reusable pieces — Sidebar, TopBar, TaskCard, modals, ui/ (badges, stat cards, etc.)
    context/           # AuthContext — client-side auth state/controller
    services/api.js    # API client (fetch wrapper, JWT header injection)
```

Backend "controllers" own all business rules (ownership checks, status
validation, duplicate-username checks, assignment permissions); "views"
(`*_views.py`) are thin route handlers that parse the request, call a
controller, and shape the JSON response; "models" only define schema and
persistence.

## End-to-end journey

This isn't just a flat task list — it models a real small-team workflow:

1. **Register / log in** (JWT-based auth, bcrypt password hashing)
2. **Onboarding**: a first-time user with no projects lands on a "create your
   first project" prompt instead of an empty dashboard
3. **Create a Project** to group related work (e.g. "Launch Plan")
4. **Add tasks** to the project with a **priority** (low/medium/high) and an
   optional **due date**
5. **Assign tasks** to any registered teammate (defaults to yourself) — the
   assignee can update the task's status even if they don't own it; only the
   project/task owner can edit title, description, or delete
6. **Track progress** on the Dashboard (stats across all your projects),
   per-project progress bars, and a dedicated **My Work** view filtered by
   status, showing everything assigned to you across every project
7. **Profile** page with account info and personal completion stats

## Running locally (no Docker)

**Backend**
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python run.py          # http://localhost:5000
```

**Frontend** (separate terminal)
```bash
cd frontend
npm install
npm run dev             # http://localhost:5173, proxies /api -> :5000
```

## Running with Docker Compose

```bash
docker compose up --build
```

- `reverse-proxy` (Nginx) → http://localhost — simulates a production entry point, routes `/api/*` to the backend and everything else to the frontend
- `frontend` also directly reachable at http://localhost:8080
- `backend` also directly reachable at http://localhost:5000
- SQLite data persists in the `backend-data` named volume

## Running tests

```bash
cd backend
source venv/bin/activate
pytest                         # or: pytest --cov=app --cov-report=term-missing

cd ../frontend
npm run lint
npm run build
```

## CI/CD (GitHub Actions)

`.github/workflows/ci.yml` runs on every push/PR to `main`:

1. **backend-lint-test** — flake8 + pytest with coverage
2. **frontend-lint-build** — oxlint + Vite production build
3. **build-images** — builds backend & frontend Docker images, uploads as artifacts
4. **integration-tests** — loads the built images, brings up the stack with
   `docker compose`, waits for the backend health check, then runs a smoke
   test (register → create task → list tasks → hit the frontend) before
   tearing the stack down

You can run the same CI locally with [`act`](https://github.com/nektos/act):
```bash
act -j backend-lint-test
act -j frontend-lint-build
```

## Kubernetes simulation (Minikube or Kind)

Manifests live in `k8s/` (namespace, Deployments, Services, a Secret, an
Ingress, and a `kustomization.yaml`).

```bash
# Minikube
minikube start
minikube addons enable ingress
eval $(minikube docker-env)         # build images into Minikube's Docker daemon
docker build -t task-manager-backend:local ./backend
docker build -t task-manager-frontend:local ./frontend

# Kind
kind create cluster
docker build -t task-manager-backend:local ./backend
docker build -t task-manager-frontend:local ./frontend
kind load docker-image task-manager-backend:local
kind load docker-image task-manager-frontend:local
# install ingress-nginx separately for Kind, then apply the ingress class

# Apply manifests (either platform)
kubectl apply -k k8s/

kubectl -n task-manager get pods
echo "127.0.0.1 task-manager.local" | sudo tee -a /etc/hosts   # or use minikube tunnel
minikube tunnel   # (Minikube only, in a separate terminal, for LoadBalancer/Ingress access)
```

Then visit `http://task-manager.local`.

**Note:** the backend Deployment is intentionally kept at `replicas: 1`
because SQLite on a single `ReadWriteOnce` volume doesn't support safe
concurrent writes across pods — swap `DATABASE_URL` to a PostgreSQL
connection string (and add a `postgres` Deployment/Service) to scale the
backend horizontally.

## Reverse proxy

- `frontend/nginx.conf` — bundled with the frontend Docker image; serves the
  built SPA and proxies `/api/*` to the `backend` service
- `nginx/nginx.conf` — standalone top-level reverse proxy (used by
  `docker-compose`'s `reverse-proxy` service) fronting both `frontend` and
  `backend`, simulating a single production entry point on port 80

## Environment variables

| Variable       | Where             | Default                                   |
|----------------|-------------------|---------------------------------------------|
| `SECRET_KEY`   | backend            | `dev-secret-key-change-in-prod` (override in production) |
| `DATABASE_URL` | backend            | `sqlite:///backend/instance/tasks.db`     |
| `VITE_API_BASE_URL` | frontend (dev)| `/api`                                     |
