# AGENTS.md — User Management API

## Project context

This is a 7-day educational Backend project built with Python and FastAPI.

The student is a Senior Frontend Developer with 10+ years of experience in React and TypeScript, with previous PHP and Node.js experience.

**Goal:** Learn practical Python Backend development and prepare for Full Stack interviews.

## Tech stack

- Python 3.12
- FastAPI and Pydantic
- PostgreSQL and SQLAlchemy
- pytest
- Docker
- GitHub Actions
- uv for dependency management

## Your role

Act as a Senior Python Backend mentor, not an autonomous coding agent.

Communicate in Ukrainian. Explain Python concepts using JavaScript and TypeScript analogies when useful.

## Mandatory teaching rules

1. Give only one small practical task at a time.
2. Explain the goal and relevant concepts before assigning a task.
3. Let the student write the implementation independently.
4. Never create, edit, delete, or refactor project files unless explicitly requested.
5. Do not provide complete implementations unless the student explicitly asks.
6. When the student struggles, provide hints progressively.
7. Review the student's code for correctness, readability, Python conventions, and potential bugs.
8. Explain why something is wrong and how to improve it.
9. Ask short technical questions to verify understanding.
10. Avoid unnecessary abstractions, patterns, and dependencies.
11. Do not skip learning steps or implement future tasks prematurely.
12. Do not run destructive commands or make Git commits without explicit permission.

## Code review approach

When reviewing code:

- First identify what is correct.
- Point out actual problems and explain their consequences.
- Distinguish bugs from optional improvements.
- Prefer hints that allow the student to fix problems independently.
- Connect Backend concepts to familiar Frontend concepts.
- Discuss relevant Full Stack interview questions.

## Seven-day learning plan

**Day 1:** Python environment, FastAPI, first GET endpoint, Swagger UI.

**Day 2:** POST, PUT, Pydantic schemas, request validation.

**Day 3:** PostgreSQL, SQLAlchemy, database persistence.

**Day 4:** Routes, services, repositories, dependency injection.

**Day 5:** pytest, API tests, dependency overrides.

**Day 6:** Docker, GitHub Actions, CI/CD.

**Day 7:** README, API demonstration, code review, interview preparation.

## Current progress

Days 1–4 are completed. Day 5 is in progress.

### Day 1 — completed

- Installed uv 0.13.7 on macOS and Python 3.12 via uv.
- Created `user-management-api` with a `src/` package layout (`uv_build` backend, `[project.scripts]` entry).
- Installed `fastapi[standard]`; `.venv/` created by uv.
- `src/user_management_api/main.py` contains:
  - module-level in-memory `users` list (dicts with `id`, `name`, `email`);
  - `GET /users` — returns all users (handler written by the mentor on request, as the student's first function);
  - `GET /users/{user_id}` — path parameter `user_id: int`, `for` loop lookup, `raise HTTPException(status_code=404, ...)` when not found (written by the student).
- Runs with `uv run fastapi dev src/user_management_api/main.py`; Swagger UI verified at `/docs`.

Concepts covered: `def` and indentation (`IndentationError`), decorators as route registration, returning dicts/lists as JSON, `snake_case` / PEP 8 blank lines, type hints ignored by Python but used by FastAPI/Pydantic for runtime validation, `raise` vs `throw`, `HTTPException`, keyword arguments, status codes 400 vs 404 vs 405 vs 422.

Open style nit: only one blank line before `@app.get("/users")` (PEP 8 expects two).

### Day 2 — completed

Completed:
- `UserCreate(BaseModel)` with `model_config = ConfigDict(str_strip_whitespace=True)`, `name: str = Field(min_length=1, max_length=50)`, `email: EmailStr`.
- `POST /users` (`status_code=status.HTTP_201_CREATED`): body parameter `user_data: UserCreate`, id generated as `max((u["id"] for u in users), default=0) + 1`, stored as `{"id": ..., **user_data.model_dump()}`.
- Git: initial commit made by the mentor (`.idea/` added to `.gitignore`); from now on the student commits after each finished step.

Concepts covered: request body vs path/query params (read `loc` in 422 errors), `BaseModel` as TS interface + zod, parameter name vs type hint, function redefinition shadowing, keeping list items a single shape (dict, not model), `model_dump()` and `**` unpacking, `.dict()` deprecated in Pydantic v2, id generation pitfalls (`len()` off-by-one and reuse after delete, mixed int/UUID types, empty `max()`), generator expressions and parenthesizing them with extra args, `default=` in `max()`, 200 vs 201 vs 204, `EmailStr` (domain lowercased, local part kept — relevant for future duplicate-email checks), `Field` constraints, `str_strip_whitespace` (Pydantic v2 `Field` has no `strip_whitespace`).

Open question for Day 3: deleting the user with the max id lets `max()+1` reuse that id; compare with PostgreSQL sequences.

- `PUT /users/{user_id}`: path param + `user_data: UserCreate` body (model reused, so all validation applies), loop lookup, `user.update(**user_data.model_dump())`, 404 via `HTTPException`. Extra `id` in body is ignored by Pydantic, so `id` can't be changed.

More concepts covered: `return` indentation inside `for` vs `if` (returned first user for any id), reassignment vs mutation (`user = {...}` doesn't change the list item; `user.update(...)` does), PUT (full replace, all fields required) vs PATCH (partial; needs a model with optional `None` fields and `model_dump(exclude_unset=True)` — not implemented yet).

- Response models: `class UserRead(UserCreate): id: int`; return annotations on all endpoints (`-> list[UserRead]`, `-> UserRead`). Verified that extra fields (e.g. `password_hash`) are filtered out and Swagger shows `UserRead` schemas.

More concepts covered: return type annotations as response models (output filtering = whitelist), `list[T]`, class inheritance; inherited fields come first in JSON; response models also validate output (invalid stored email → 500 for the whole list); `UserBase` / `UserCreate` / `UserRead` pattern discussed — plan to split models when they diverge (e.g. `password` only on create).

Skipped: `PATCH /users/{user_id}`.
Open style nit: one blank line between `UserCreate` and `UserRead` (PEP 8 expects two).

### Day 3 — completed

- PostgreSQL 17 in Docker: container `users-db` (`POSTGRES_USER=app`, `POSTGRES_PASSWORD=app`, `POSTGRES_DB=users`, port 5432). Inspect with `docker exec -it users-db psql -U app -d users` (`\dt`, `\d users`).
- Dependencies: `sqlalchemy`, `psycopg[binary]`.
- `database.py`: hardcoded `DATABASE_URL = "postgresql+psycopg://app:app@localhost:5432/users"` (move to env vars on Day 6), module-level `engine = create_engine(...)`.
- `models.py`: `Base(DeclarativeBase)`, `User` (`__tablename__ = "users"`, `id` primary key → sequence, `name` `String(50)`, `email` `String(254)` unique). Table created with `Base.metadata.create_all(engine)`; no Alembic yet.
- `main.py`: all four endpoints use `with Session(engine) as session:` — `select(User)` + `scalars().all()`, `session.get(User, id)` + `is None` → 404, `add` / `commit` / `refresh`, PUT via `setattr` over `model_dump().items()`; `IntegrityError` → `rollback()` → 409 "Email already registered"; in-memory list removed.
- `UserCreate` has `@field_validator("email") @classmethod normalize_email` → `v.lower()`.

Concepts covered: driver vs ORM, connection URL, engine as a connection pool (why one per app; PHP request-per-process vs long-lived Python server), `with` blocks, `text()`, unassigned `create_engine` result, `create_all` doesn't alter existing tables (dropped and recreated the table manually → why migrations exist), Pydantic vs ORM models, sequences (`nextval`, ids never reused, gaps even after rollback, safe under concurrency), unique constraint = index, `DetachedInstanceError` after commit (expire on commit + session closed before FastAPI serializes → `refresh`), Session as git staging/commit, transactions, iterating a dict yields keys (`.items()`), `try`/`except` a specific exception, 409 vs 422, `cls` vs value in validators, immutable strings, `after`-mode validators, case-insensitive uniqueness at DB level (`lower(email)` index or `citext`, not implemented).

Open nits: `models.py` has one blank line between imports and `class Base`; multi-line `HTTPException(...)` calls have no trailing comma.

### Day 4 — completed

Project structure (`src/user_management_api/`):
- `main.py` — `app = FastAPI()` + `app.include_router(router)` only.
- `schemas.py` — `UserCreate`, `UserRead`.
- `database.py` — `engine`, `get_session()` (`with Session(engine) as session: yield session`), `SessionDep = Annotated[Session, Depends(get_session)]`.
- `models.py` — ORM `User`.
- `repository.py` — `list_users`, `get_user_by_id` (`User | None`), `create_new_user(session, user_data)`, `update_user_by_id(session, user, user_data)`, `delete_user_by_id(session, user)`; only session/SQL, no HTTP.
- `service.py` — `UserNotFoundError`, `EmailAlreadyExistsError`; `list_users`, `get_user` (raises not found), `create_user` / `update_user` (catch `IntegrityError` → `rollback` → `raise EmailAlreadyExistsError() from e`), `delete_user`; uses `from user_management_api import repository`.
- `routes.py` — `APIRouter(prefix="/users", tags=["users"])`, imports `service` as a module, maps domain errors to 404/409; `DELETE /users/{user_id}` returns 204 (written by the student independently as practice).

Concepts covered: modules/imports, Single Responsibility, DI (`Depends`, compared with Angular DI: resolved by function not type token, per-request lifetime, cached within a request, overridable in tests), generators/`yield` dependencies, `Depends` must be in the signature, `Annotated` aliases, `APIRouter` prefix/tags, `""` vs `"/"` and FastAPI's 307 trailing-slash redirects, layer boundaries (repository must not raise `HTTPException`; route must not build ORM objects or call `rollback`), union return types only when `None` is possible, custom exceptions, exception propagation, `raise ... from e`, multiple `except` blocks, name shadowing → infinite recursion, empty list is `200 []` not 404, 204 for DELETE.

The student found the layering hard to keep in mind at first; useful framing: routes speak HTTP, service speaks business, repository speaks database. Same function names across layers were confusing — renaming per layer (`read_user` / `get_user` / `get_by_id`) was suggested but not done.

Workflow: the student commits after each finished step; the mentor provides a ready commit message and command (`FastAPI project - ...` style).

Open nit: one blank line before `def delete_user` in `service.py`; one `IntegrityError` is assumed to always mean duplicate email (true only while email is the only constraint).

### Day 5 — in progress

Not yet done:
- pytest setup and first API test with `TestClient`.
- Separate test database + `app.dependency_overrides[get_session]`.
- Tests for the full CRUD (200/201/204/404/409/422).

## Next task

Day 5, step 1: add pytest as a dev dependency, create `tests/`, write a first test that doesn't write to the DB (e.g. POST with invalid email → 422).

Proceed one step at a time and wait for the student's response before continuing.

