# RedZone Gateway

A Backend Event Management API for creating events, managing RSVPs, and handling waitlists automatically - Built to explore real production infrastructure. Users can create events, RSVP, join a waitlist when an event is at capacity, and get notified with automatic email notifications built in.

Built with Django REST Framework, containerized with Docker, and deployed live on AWS.

**Live API:** http://13.218.221.131/api/events/

---

## Core Features

- Create, browse, and manage events
- RSVP to events, with automatic capacity limits
- Join a waitlist once an event is at capacity
- Automatic waitlist promotion - when someone cancels their RSVP, the next person on the waitlist is automatically confirmed and notified
- Event cancellation notifies everyone connected to it: RSVP's, waitlisted users, and the host, each with a tailored email
- Token-based authentication, with permissions ensuring only an event's owner can edit or cancel it
- Self-service endpoints: view your own events, RSVPs, and waitlist entries.

---

## Tech stack

| Layer | Tool |
|---|---|
| Framework | Django, Django REST Framework |
| Database | PostgreSQL |
| Background tasks | Celery + Redis |
| Containerization | Docker, Docker Compose |
| Reverse proxy | NGINX |
| Deployment | AWS EC2 |
| Testing | Django's built-in test framework (APITestCase) |

---

## Architecture

Client → NGINX (port 80) → Django (port 8000, internal) → PostgreSQL
                                    ↓
                                Celery → Redis → background email tasks

NGINX is used in front of Django as a reverse proxy, handling incoming traffic before it reaches the application server. Background tasks (RSVP confirmations, waitlist notifications, cancellation emails) are handled in a background queue by Celery so the API never gets blocked by a delayed email

---

## Running it locally

Requires Docker and Docker Compose installed

**1. Clone and start the stack**
```bash
git clone <this-repo>
cd redzone-gateway
docker compose up --build
```
This starts four containers: Django, PostgreSQL, Redis, and NGINX.


**2. Set up the database**
```bash
docker compose exec web python3 manage.py migrate
docker compose exec web python3 manage.py createsuperuser
```

**3. You're live & all set!**

The API is now available at `http://localhost/api/`.

---

## Running the tests

```bash
docker compose exec web python3 manage.py test events
```

Covers RSVP creation, duplicate-RSVP prevention, capacity enforcement, automatic waitlist promotion, and ownership permissions.

---

## API overview

| Endpoint | Description |
|---|---|
| `GET /api/events/` | List all events |
| `POST /api/events/` | Create an event |
| `POST /api/events/{id}/cancel/` | Cancel an event (owner only) |
| `GET /api/events/my_events/` | Events you created |
| `POST /api/rsvps/` | RSVP to an event |
| `DELETE /api/rsvps/{id}/` | Cancel your RSVP (triggers waitlist promotion if applicable) |
| `GET /api/rsvps/my_rsvps/` | Your RSVPs |
| `POST /api/waitlist/` | Join an event's waitlist |
| `GET /api/waitlist/my_waitlist/` | Your waitlist entries |
| `GET /api/waitlist/my_position/?event_id={id}` | Your position on a specific waitlist |

Full browsable API available at `/api/` when running.

## What I'd improve next

- Add HTTPS via a proper domain and SSL certificate
- Set up CI/CD so tests run automatically on push
- Add rate limiting on write endpoints

---

Built to learn backend fundamentals and understand how real backend systems are structured - not just CRUD, but the infrastructure that makes an app production-shaped: capacity limits, async notifications, container setup, and a real cloud deployment.

