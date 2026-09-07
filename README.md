# RideInfo

A Django REST Framework API for a ride-sharing platform. It manages users (admins, drivers, riders), rides, and ride events, and exposes a paginated endpoint for listing rides with filtering, sorting, and distance-based ordering.

## Features

- **Custom data model** for rides, ride events, and users with roles (`admin`, `driver`, `rider`)
- **REST API** built with Django REST Framework and `django-filter`
- **Admin-only API access** — every `/api/` endpoint requires an `admin`-role user
- **Filtering & sorting** on the rides endpoint:
  - Filter by `status`
  - Filter by `rider_email`
  - Sort by `pickup_time` (ascending/descending)
  - Sort by distance to the pickup point using the Haversine formula (requires `latitude` and `longitude`)
- **Pagination** with configurable page size
- **Optimized queries** using `select_related`, `prefetch_related`, and per-ride "today's events" (events from the last 24 hours)
- **Django admin** customization for users, rides, and ride events
- **Sample data seeder** via the `init_data` management command
- `django-debug-toolbar` included for development

## Tech Stack

| Component    | Technology                          |
| ------------ | ----------------------------------- |
| Language     | Python                              |
| Framework    | Django 5.2                          |
| API          | Django REST Framework               |
| Database     | SQLite                              |
| Filtering    | django-filter                       |
| Debugging    | django-debug-toolbar                |

## Project Structure

```
ride_info/
├── db.sqlite3               # SQLite database (generated)
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── core/                    # Main application
│   ├── admin/               # Admin classes for User, Ride, RideEvent
│   ├── management/
│   │   └── commands/
│   │       └── init_data.py # Sample data seeder
│   ├── migrations/          # Database migrations
│   ├── models/              # User, Ride, RideEvent models
│   ├── serializers/         # DRF serializers
│   └── views/
│       └── ride_views.py    # RideViewSet (API logic)
└── ride_info/               # Project settings & URL configuration
    ├── settings.py
    └── urls.py
```

## Data Models

### `User`
| Field        | Type                     | Notes                     |
| ------------ | ------------------------ | ------------------------- |
| `id_user`    | `AutoField` (PK)         |                           |
| `role`       | `CharField` (choices)    | `admin` / `driver` / `rider` |
| `first_name` | `CharField(100)`         |                           |
| `last_name`  | `CharField(100)`         |                           |
| `email`      | `EmailField` (unique)    |                           |
| `phone_number` | `CharField(20)`        |                           |

### `Ride`
| Field              | Type                       | Notes                          |
| ------------------ | -------------------------- | ------------------------------ |
| `id_ride`          | `AutoField` (PK)           |                                |
| `status`           | `CharField` (choices)      | `pending`, `en-route`, `pickup`, `dropoff`, `completed`, `cancelled` |
| `id_rider`         | `FK → User`                | `related_name="rides_as_rider"` |
| `id_driver`        | `FK → User`                | `related_name="rides_as_driver"` |
| `pickup_latitude`  | `FloatField`               |                                |
| `pickup_longitude` | `FloatField`               |                                |
| `dropoff_latitude` | `FloatField`               |                                |
| `dropoff_longitude`| `FloatField`               |                                |
| `pickup_time`      | `DateTimeField` (indexed)  |                                |

### `RideEvent`
| Field           | Type                   | Notes                    |
| --------------- | ---------------------- | ------------------------ |
| `id_ride_event` | `AutoField` (PK)       |                          |
| `id_ride`       | `FK → Ride`            | `related_name="ride_events"` |
| `description`   | `CharField(200)`       |                          |
| `created_at`    | `DateTimeField`        | Auto-set on creation     |

## API Reference

### Authentication

All `/api/` endpoints are restricted to users with the `admin` role on the custom `User` model:

1. Send the `X-User-Id` header containing the `id_user` of the calling user.
2. The `IsAdminRole` permission then checks that the user's `role` is `admin`.

| Header      | Value                                  |
| ----------- | -------------------------------------- |
| `X-User-Id` | `id_user` of a row in the `User` model |

| Response | Meaning                                      |
| -------- | -------------------------------------------- |
| `200`    | User exists and has the `admin` role         |
| `401`    | `X-User-Id` header missing or matches no user |
| `403`    | User exists but their role is not `admin`    |

> Note: `core.User` is a plain data model (separate from Django's built-in auth users), so this header lookup stands in for real authentication. Swap it for token/session auth in production.

### List rides

```
GET /api/rides/
```

Returns a paginated list of rides. Each ride includes its rider, driver, today's ride events (from the last 24 hours), and an optional `distance_to_pickup` field (in km, only present when sorting by distance).

#### Query Parameters

| Parameter     | Description                                                                 |
| ------------- | --------------------------------------------------------------------------- |
| `status`      | Filter rides by status (e.g. `?status=completed`)                           |
| `rider_email` | Filter rides by the rider's email (e.g. `?rider_email=rider1@example.com`)  |
| `sort`        | `pickup_time`, `-pickup_time`, `distance`, or `-distance`                   |
| `latitude`    | Required with `sort=distance` / `sort=-distance` — reference latitude       |
| `longitude`   | Required with `sort=distance` / `sort=-distance` — reference longitude      |
| `page_size`   | Number of results per page (default `10`, max `100`)                        |
| `page`        | Page number                                                               |

#### Examples

```bash
# All rides (page 1, 10 per page) — as an admin user
curl -H "X-User-Id: 1" "http://localhost:8000/api/rides/"

# Completed rides sorted by pickup time (descending)
curl -H "X-User-Id: 1" "http://localhost:8000/api/rides/?status=completed&sort=-pickup_time"

# Rides sorted by distance to a reference point
curl -H "X-User-Id: 1" "http://localhost:8000/api/rides/?sort=distance&latitude=37.5&longitude=-122.0"

# 25 results per page
curl -H "X-User-Id: 1" "http://localhost:8000/api/rides/?page_size=25&page=2"
```

#### Response Shape

```json
{
    "count": 30,
    "next": "http://localhost:8000/api/rides/?page=2",
    "previous": null,
    "results": [
        {
            "id_ride": 1,
            "status": "completed",
            "rider": {
                "id_user": 5,
                "role": "rider",
                "first_name": "Rider1",
                "last_name": "User",
                "email": "rider1@example.com",
                "phone_number": "3134567890"
            },
            "driver": {
                "id_user": 2,
                "role": "driver",
                "first_name": "Driver1",
                "last_name": "User",
                "email": "driver1@example.com",
                "phone_number": "2134567890"
            },
            "todays_ride_events": [
                {
                    "id_ride_event": 1,
                    "id_ride": 1,
                    "description": "Ride completed",
                    "created_at": "2026-09-06T10:00:00Z"
                }
            ],
            "pickup_latitude": 37.75,
            "pickup_longitude": -122.4,
            "dropoff_latitude": 37.79,
            "dropoff_longitude": -122.35,
            "pickup_time": "2026-09-06T09:30:00Z",
            "distance_to_pickup": 12.45
        }
    ]
}
```

### Using Postman

1. Create a new request:
   - Method: `GET`
   - URL: `http://localhost:8000/api/rides/?status=completed&sort=-pickup_time`
2. Open the **Headers** tab and add a header:
   - Key: `X-User-Id`
   - Value: `1` (the `id_user` of the admin seeded by `init_data`)
3. Click **Send** and check the response:
   - `200 OK` — the user has the `admin` role; the paginated ride list is returned.
   - `401 Unauthorized` — the header is missing or doesn't match any user.
   - `403 Forbidden` — the user exists but isn't an admin (e.g. a driver or rider id).

Tips:

- Find admin ids in the Django admin at `http://localhost:8000/admin/core/user/`, or run:

  ```bash
  python manage.py shell -c "from core.models import User; print(list(User.objects.filter(role='admin').values_list('id_user', flat=True)))"
  ```

- Save the `X-User-Id` header at the collection level in Postman to reuse it across requests.

## Getting Started

### Prerequisites

- Python 3.10+ (project was created with Django 5.2.7)
- `pip`

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/karimjordanbuenaseda/RideInfo.git
cd RideInfo/ride_info

# 2. (Optional but recommended) Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database migrations
python manage.py migrate

# 5. (Optional) Seed the database with sample data
python manage.py init_data

# 6. Run the development server
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/rides/` and the admin interface at `http://localhost:8000/admin/`.

### Seeding Sample Data

The `init_data` management command creates a realistic dataset:

- 1 admin, 20 drivers, and 40 riders
- 30 rides with randomized statuses, pickup times (±3 days), and coordinates (San Francisco Bay Area)
- 2–5 ride events per ride

| Command                           | Description                                              |
| --------------------------------- | -------------------------------------------------------- |
| `python manage.py init_data`      | Create sample data (without cleaning existing data)      |
| `python manage.py init_data --clean` | Delete all existing data before seeding               |
| `python manage.py init_data --rides` | Create rides and events only (no users)               |

## Admin Interface

The Django admin (`/admin/`) provides custom views for all three models:

- **Users** — search by name/email, filter by role
- **Rides** — filter by status
- **Ride Events** — search by description, filter by ride

Note: the sample data is created in the custom `User` model, which is separate from Django's built-in auth users. Create a Django superuser with `python manage.py createsuperuser` to log into the admin.

## Development

- `django-debug-toolbar` is available when `DEBUG = True` (add `"debug_toolbar"` to `INSTALLED_APPS` and its middleware to `MIDDLEWARE` in `settings.py` if you want the toolbar panels to render).
- `ALLOWED_HOSTS` currently allows `localhost` and `127.0.0.1` only — suitable for development, not production.

## Configuration

Key settings live in `ride_info/settings.py`:

| Setting        | Value                                |
| -------------- | ------------------------------------ |
| `DEBUG`        | `True`                               |
| `ALLOWED_HOSTS`| `localhost`, `127.0.0.1`             |
| `DATABASES`    | SQLite at `BASE_DIR / "db.sqlite3"`  |
| `TIME_ZONE`    | `UTC`                                |
