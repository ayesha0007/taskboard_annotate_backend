# Flowdeck — Backend

Django REST API powering Flowdeck: a combined Kanban task board (with a
per-task document editor) and an image annotation workspace.

## Tech Stack

- Python 3.12
- Django 5.0.7
- Django REST Framework 3.15.2
- djangorestframework-simplejwt 5.3.1 (JWT authentication with refresh)
- django-cors-headers 4.4.0
- Pillow 10.4.0 (image handling)
- django-filter 24.2
- SQLite by default, swappable via `DATABASE_URL` (dj-database-url)
- gunicorn + whitenoise for production serving

## Getting Started

### Prerequisites

- Python 3.12.x
- pip

### Setup

```bash
git clone <backend-repo-url>
cd <backend-repo>
python -m venv venv
source venv/bin/activate        
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin access
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/v1/`.

### Environment Variables

See `.env.example` for the full list. Key variables:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django cryptographic secret. Generate a new one for production (`python -c "import secrets; print(secrets.token_urlsafe(50))"`). |
| `DEBUG` | Set to `False` in production. |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts. |
| `CORS_ALLOWED_ORIGINS` | Comma-separated list of allowed frontend origins. |
| `DATABASE_URL` | Optional; leave empty to use local SQLite. |
| `ACCESS_TOKEN_LIFETIME_MINUTES` / `REFRESH_TOKEN_LIFETIME_DAYS` | JWT lifetimes. |

## Project Structure

backend/
├── manage.py
├── requirements.txt
├── config/                 # project settings, root URLconf, WSGI/ASGI
│   ├── settings.py
│   └── urls.py
└── apps/
├── users/               # authentication (JWT login/refresh)
├── tasks/               # Kanban task CRUD, deadlines, document content
└── annotations/         # image upload, classes, polygon/box/pen shapes
(each app: models.py, serializers.py, views.py, urls.py, migrations/)
## API Overview

- `POST /api/v1/auth/login/`, `POST /api/v1/auth/refresh/`
- `GET/POST /api/v1/tasks/` — optional `?date=YYYY-MM-DD` filter; omitted
  returns all of the authenticated user's tasks
- `GET/PATCH/DELETE /api/v1/tasks/{id}/`
- `GET/POST /api/v1/annotations/images/`
- `GET/PATCH/DELETE /api/v1/annotations/images/{id}/`
- `GET/POST/PATCH/DELETE /api/v1/annotations/polygons/`
- `GET/POST/PATCH/DELETE /api/v1/annotations/classes/`

All endpoints except auth require a valid JWT and are scoped to the
authenticated user via `owner`.

## Data Model Notes

- `Task.due_date` + `Task.due_time` (optional) together form the deadline.
- `Task.content` stores the rich-text HTML written in the frontend's
  per-task document editor; `Task.sketch_data` stores a base64 PNG of the
  freehand sketch layer.
- `Polygon.points` is a list of `[x, y]` pairs normalized to `0–1` against
  the *source image's own dimensions* (not any particular UI container),
  so annotations remain correct regardless of how the frontend renders
  them.

## Challenges & Solutions

**Annotation coordinates tied to the display container instead of the
image.** Early on, annotation points were normalized against the on-screen
canvas element, which letterboxes non-16:9 images. This worked for
drawing and displaying overlays (since the same container was used for
both), but broke cropped-thumbnail generation, which needs coordinates in
image space. Resolved on the frontend by normalizing points against the
image's actual rendered content instead of the container; no backend
change was required since `Polygon.points` was already just opaque
normalized floats.

**Deadlines conflicting with day-filtered task views.** Once `Task` grew
optional `due_time` and tasks could be created for any future date, the
frontend's day-scoped board view made new tasks for other days appear to
vanish. No backend fix was needed here — the `?date=` filter on
`TaskViewSet.get_queryset` was already optional, so making the filter
optional client-side (default: all tasks) resolved it without an API
change.

**Verifying data loss vs. display bugs.** When a reported "tasks
disappearing" bug turned out to be a frontend display issue, the fastest
way to rule out a backend persistence bug was `python manage.py shell`
against the `Task` queryset directly, confirming the rows existed with
correct field values before spending time on frontend fixes.

**JWT refresh race conditions.** Concurrent requests hitting a 401 while
a token refresh is already in flight are queued on the frontend and
replayed once the new access token is available, avoiding duplicate
refresh calls and inconsistent auth state.

## Development Notes

Parts of this project were built with the assistance of Claude (Anthropic)
for scaffolding, debugging, and code review, alongside the official Django
and Django REST Framework documentation for API design and JWT
authentication setup. All generated code was reviewed, tested, and
adjusted before being committed.


## Demo Credentials

- Email: `nisa@gmail.com`
- Password: `12345`

## Running the Project

### Backend (Django)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```
