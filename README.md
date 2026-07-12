# Task Board + Annotation Tool — Backend (Django REST API)

Django REST Framework API powering two modules:
1. **Tasks** — a date-scoped Kanban board (`/api/v1/tasks/`)
2. **Annotations** — image upload + polygon drawing storage (`/api/v1/annotations/`)

Auth is email/password based, using JWT (access + refresh tokens).

## Tech stack

- Python 3.12
- Django 5.0 + Django REST Framework
- SimpleJWT for authentication
- SQLite by default (swap to Postgres via `DATABASE_URL` — no code changes needed)

## Project structure

```
backend/
├── config/            # settings, root urls, wsgi/asgi
└── apps/
    ├── users/          # custom email-based User model + JWT login
    ├── tasks/          # Kanban Task model + CRUD API
    └── annotations/    # image upload + polygon CRUD API
```

## Getting started

```bash
# 1. create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. install dependencies
pip install -r requirements.txt

# 3. configure environment variables
cp .env.example .env
# open .env and set a real SECRET_KEY

# 4. run migrations
python manage.py migrate

# 5. create an admin/demo user
python manage.py createsuperuser

# 6. run the dev server
python manage.py runserver
```

API will be available at `http://127.0.0.1:8000/api/v1/`.

## Key endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/login/` | Login with `email` + `password`, returns JWT pair |
| POST | `/api/v1/auth/refresh/` | Refresh an access token |
| GET | `/api/v1/auth/me/` | Current authenticated user |
| GET/POST | `/api/v1/tasks/?date=YYYY-MM-DD` | List/create tasks for a date |
| PATCH/DELETE | `/api/v1/tasks/{id}/` | Update (e.g. drag-and-drop status/position) or delete a task |
| GET/POST | `/api/v1/annotations/images/` | List / upload images (multipart) |
| GET/POST | `/api/v1/annotations/polygons/?image={id}` | List / create polygons for an image |
| DELETE | `/api/v1/annotations/polygons/{id}/` | Remove one polygon |

All endpoints except login require an `Authorization: Bearer <token>` header.

## Security notes

- Custom `User` model authenticates by email, passwords are hashed by Django's PBKDF2 hasher.
- Every queryset is scoped to `request.user` — one user can never read or mutate another user's tasks, images, or polygons.
- Uploaded images are validated for content-type (`jpeg/png/webp`) and size (max 5MB).
- Polygon point data is validated server-side (min 3 points, normalized 0–1 coordinates) so bad data from a buggy frontend can't corrupt the database.
- `DEBUG=False` in production automatically turns on HSTS, secure cookies, and SSL redirect (see `config/settings.py`).
- Login endpoint is rate-limited (`10/min`) via DRF throttling to slow down brute-force attempts.

## Difficulties faced & how they were solved

- **Custom user model with email login**: Django's default `User` uses `username`. Swapping the `USERNAME_FIELD` to `email` required a custom `UserManager` (for `createsuperuser`/`create_user`) — solved by subclassing `AbstractBaseUser` + `PermissionsMixin` directly instead of fighting the default model.
- **Keeping annotation coordinates resolution-independent**: storing raw pixel coordinates would break if the frontend rendered the image at a different size. Solved by normalizing all polygon points to a 0–1 range relative to image width/height, validated in the serializer.
- **Preventing cross-user data leaks on nested resources**: a polygon references an image, but that image's ownership had to be re-checked on create (not just on the queryset) — otherwise a user could attach a polygon to *someone else's* image ID. Solved with an explicit ownership check in `perform_create`.

## Environment variables

See `.env.example` for the full list (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `DATABASE_URL`, JWT lifetimes).
