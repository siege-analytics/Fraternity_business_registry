# Fraternity-Owned Business Registry

A GeoDjango application for cataloging businesses owned or operated by
fraternity/sorority members, local chapters, or national organizations, with
full spatial support for "find nearby" queries, census-unit assignment, and
mapping. Built on the GeoDjango Simple Template (see below).

## What's in this project

The `businesses` Django app models:

- **Council** — governing bodies such as NIC, NPC, NPHC, NALFO, NAPA, NMGC, PFA.
- **Fraternity** — a Greek-letter organization (social, professional, honor,
  service, religious, multicultural, etc.), with council affiliation, founding
  info, and an optional headquarters address.
- **Chapter** — a local chapter of a fraternity, tied to an institution or
  alumni city, with status, charter year, optional address, and a point
  geometry for the chapter house.
- **BusinessCategory** — a hierarchical taxonomy of business types.
- **Business** — a business owned/controlled by a fraternity, chapter, or
  member. Has a point geometry, address, category, operating status,
  verification flag, and contact info.
- **BusinessOwnership** — a join row connecting a business to one or more
  owning fraternities / chapters / named members, with role (founder, owner,
  co-owner, investor, operator) and optional ownership percentage.

Addresses reuse `locations.United_States_Address` so businesses and chapters
inherit the template's built-in geocoding and census-unit assignment.

### REST API

Once the stack is up (see Quick Start below):

```
GET  /businesses/councils/
GET  /businesses/fraternities/?fraternity_type=social_fraternity&council=1
GET  /businesses/chapters/?fraternity=3&status=active
GET  /businesses/categories/
GET  /businesses/businesses/?ownership_class=chapter&verified=true
GET  /businesses/businesses/nearby/?lat=37.77&lon=-122.41&radius_km=10
GET  /businesses/ownerships/?fraternity=3
```

All list endpoints that include a geometry return GeoJSON
`FeatureCollection`s (via `GeoFeatureModelSerializer`) so they drop straight
into Leaflet / Mapbox / MapLibre front-ends.

### Getting started with this app

```bash
make build && make up
make shell
python hellodjango/manage.py makemigrations businesses
python hellodjango/manage.py migrate
python hellodjango/manage.py createsuperuser
# then visit http://localhost:8000/admin/ to seed councils, fraternities,
# chapters, categories, businesses, and ownerships.
```

---

# GeoDjango Simple Template

A production-ready template for building GeoDjango applications with spatial data support, REST APIs, and real-time capabilities.

## Tech Stack

### Core Components
- **Django 5.2** with GeoDjango
- **Daphne** - ASGI server (supports WSGI + WebSockets)
- **PostGIS** - Spatial database
- **nginx** - Reverse proxy
- **Django REST Framework** + GIS extensions
- **Grappelli** - Enhanced Django admin

### Frontend (Optional)
- **Vue 3** + Vite
- **NVM** for Node.js version management

## Quick Start

```bash
# Build and start all services
make build
make up

# Access the application
# Django API:  http://localhost:8000/locations/places/
# Nginx:       http://localhost:8001
# Admin:       http://localhost:8000/admin/
# PostGIS:     localhost:54322
```

## Load Sample Data

```bash
# Shell into webserver container
make shell

# Load standard spatial data (GADM, timezones)
python hellodjango/manage.py fetch_and_load_standard_spatial_data

# Create sample places
python hellodjango/manage.py create_sample_places

# Load Census TIGER data
python hellodjango/manage.py fetch_and_load_census_tiger_data
```

## Census & Electoral Data (NEW!)

### Voter Tabulation Districts (VTDs)

VTDs are the **smallest geographic units** for election results. Essential for precinct-level analysis and voter geography.

**Years Available:** 2010, 2020 (covers 2020-2025 FEC data)

```bash
make shell

# Fetch VTDs for a single state (CA = 06)
python hellodjango/manage.py fetch_census_vtds --year 2020 --state 06

# Fetch for ALL 50 states + DC (use Celery!)
python hellodjango/manage.py fetch_census_vtds --year 2020 --all-states --async

# Fetch both 2010 and 2020
python hellodjango/manage.py fetch_census_vtds --year 2010 --all-states --async
python hellodjango/manage.py fetch_census_vtds --year 2020 --all-states --async
```

**Celery Monitoring:**
```bash
# Via Flower UI
open http://localhost:5555

# Via terminal
docker logs -f geodjango_celery_1
```

### Address Geocoding & Census Unit Assignment

Every address can be **geocoded** (lat/lon) and **assigned to census units** (state, county, tract, block group, VTD, congressional district).

```python
# In Django shell
from locations.models import United_States_Address

# Geocode an address (uses Census Geocoder API)
from locations.tasks import geocode_address
result = geocode_address.delay(address_id=123)

# Assign census units via spatial join (requires VTDs loaded)
from locations.tasks import assign_census_units_to_address
result = assign_census_units_to_address.delay(address_id=123, year=2020)

# Batch process (parallel across workers)
from locations.tasks import geocode_addresses_batch, assign_census_units_batch
address_ids = [1, 2, 3, 4, 5]

# Step 1: Geocode all addresses
geocode_result = geocode_addresses_batch.delay(address_ids)

# Step 2: Assign census units to all geocoded addresses
units_result = assign_census_units_batch.delay(address_ids, year=2020)
```

**Use Cases:**
- "Show me donations from CA-12"
- "Which VTD is this donor in?"
- "Donations by block group"
- Voter registration vs fundraising correlation

**Data Size:**
- ~8 GB per year (both 2010 + 2020 = 16 GB)
- ~12 hours to load all states (with Celery parallelization)

## Celery (Idiot‑Proof Guide)

Use Celery workers to split big/slow tasks across multiple containers so the web app stays fast.

### 1) Start everything

```bash
make build
make up

# You should see these services running:
# - geodjango_webserver (Daphne)
# - geodjango_postgis (PostGIS)
# - geodjango_redis (Redis)
# - geodjango_celery_1, geodjango_celery_2, geodjango_celery_3 (Celery workers)
```

### 2) Run heavy commands ASYNC (don’t block your terminal)

```bash
make shell

# Load spatial data in the background (parallelized across 3 workers)
python hellodjango/manage.py fetch_and_load_standard_spatial_data --async

# Load Census TIGER data in the background
python hellodjango/manage.py fetch_and_load_census_tiger_data --async

# Create sample data in the background
python hellodjango/manage.py create_sample_places --async
```

You’ll get back a Task ID immediately. Work happens on the workers.

### 3) How to tell if workers are alive

```bash
# See workers listed
docker ps | grep geodjango_celery

# See a worker become ready
docker logs geodjango_celery_1 | grep ready

# Inspect workers (registered tasks, stats)
docker exec geodjango_celery_1 /opt/venv/bin/celery -A hellodjango inspect stats
docker exec geodjango_celery_1 /opt/venv/bin/celery -A hellodjango inspect registered
```

### 4) Watch task progress (no UI)

```bash
# Stream logs from all workers in separate terminals
docker logs -f geodjango_celery_1
docker logs -f geodjango_celery_2
docker logs -f geodjango_celery_3

# See currently running tasks
docker exec geodjango_celery_1 /opt/venv/bin/celery -A hellodjango inspect active
```

### 5) Submit tasks from Python (advanced, still idiot‑proof)

```python
from locations.tasks import fetch_and_load_standard_spatial_data_async

result = fetch_and_load_standard_spatial_data_async.delay(['gadm', 'timezone'])
print(result.id)      # Task ID
print(result.status)  # PENDING → STARTED → SUCCESS/FAILURE

# (Optional) wait for result (blocks)
result.get(timeout=900)
```

### 6) Optional: Web UI with Flower

Flower gives you a dashboard to see tasks, states, and workers.

Steps:
- Flower is included as a service; just bring the stack up.
- Open Flower: http://localhost:5555

What you’ll see:
- Workers online/offline
- Task list with live states
- Per‑task details, retries, errors

If the UI isn’t reachable, run:

```bash
make up
docker logs -f geodjango_flower
```

### FAQ

- "It looks stuck." → Check `docker logs -f geodjango_celery_1` for progress. Big downloads/unzips take time.
- "I want to use all workers." → You already are. Tasks are split automatically.
- "How do I retry?" → Re‑run the manage.py command with `--async`. Failed tasks are independent.

## Writing Your Own Celery Tasks

This template uses **Celery** for distributed task processing. Here's how to create your own tasks.

### 1) Where to Put Tasks

Tasks live in `<app_name>/tasks.py`. For the `locations` app, that's:

```
app/hellodjango/locations/tasks.py
```

Celery autodiscovers tasks from `tasks.py` files in all installed Django apps (no manual registration needed).

### 2) Simple Task Example

```python
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_data(self, dataset_name):
    """
    Simple task that processes some data
    
    Args:
        self: Task instance (because bind=True)
        dataset_name: Name of dataset to process
    
    Returns:
        dict: Results summary
    """
    try:
        logger.info(f"[Worker {self.request.hostname}] Processing {dataset_name}")
        
        # Your processing logic here
        result = do_some_work(dataset_name)
        
        return {
            'status': 'success',
            'dataset': dataset_name,
            'records_processed': result.count,
            'worker': self.request.hostname
        }
    
    except Exception as e:
        logger.error(f"Task failed: {e}")
        return {'status': 'error', 'error': str(e)}
```

**Key Points:**
- `@shared_task`: Makes the task reusable across multiple Celery apps
- `bind=True`: Gives you access to `self.request` (task ID, hostname, retries, etc.)
- Return a dict: Makes results easy to inspect
- Log worker hostname: Helps debug distributed processing

### 3) Parallel Task Patterns

#### Pattern A: Run Multiple Independent Tasks (Group)

```python
from celery import shared_task, group

@shared_task
def process_layer(layer_name):
    # Process one layer
    return {'layer': layer_name, 'count': 1000}

@shared_task
def process_all_layers():
    """Run tasks in parallel across all workers"""
    layers = ['layer_0', 'layer_1', 'layer_2', 'layer_3']
    
    # Create a group of parallel tasks
    job = group(process_layer.s(layer) for layer in layers)
    result = job.apply_async()
    
    # Wait for all to complete (optional)
    results = result.get(timeout=300)
    return results
```

#### Pattern B: Chain Tasks (Sequential)

```python
from celery import shared_task, chain

@shared_task
def download_file(url):
    return {'path': '/tmp/data.zip'}

@shared_task
def extract_file(download_result):
    path = download_result['path']
    return {'extracted': '/tmp/data/'}

@shared_task
def process_file(extract_result):
    return {'status': 'complete'}

@shared_task
def full_pipeline(url):
    """Chain tasks - output of each becomes input of next"""
    workflow = chain(
        download_file.s(url),
        extract_file.s(),
        process_file.s()
    )
    return workflow.apply_async()
```

#### Pattern C: Parallel → Callback (Chord)

```python
from celery import shared_task, group, chord

@shared_task
def preprocess_chunk(chunk_id):
    """Process one chunk (runs in parallel)"""
    return {'chunk': chunk_id, 'records': 5000}

@shared_task
def finalize_results(preprocess_results):
    """Called after ALL preprocessing completes"""
    total = sum(r['records'] for r in preprocess_results)
    return {'status': 'complete', 'total_records': total}

@shared_task
def process_with_finalization():
    """Run parallel tasks, then a callback when ALL are done"""
    workflow = chord(
        group(preprocess_chunk.s(i) for i in range(10))
    )(finalize_results.s())
    
    return workflow.apply_async()
```

### 4) Calling Tasks

```python
# Fire and forget (returns immediately)
result = process_data.delay('my_dataset')
print(result.id)  # Task ID

# Advanced call with options
result = process_data.apply_async(
    args=['my_dataset'],
    countdown=60,           # Delay 60 seconds before starting
    retry=True,             # Auto-retry on failure
    retry_policy={
        'max_retries': 3,
        'interval_start': 0,
        'interval_step': 0.2,
        'interval_max': 0.2,
    }
)

# Wait for result (blocks!)
try:
    output = result.get(timeout=300)  # 5 min timeout
    print(output)
except Exception as e:
    print(f"Task failed: {e}")
```

### 5) Best Practices

#### ✅ DO

- **Use `bind=True`** to access task metadata (`self.request.hostname`, `self.request.id`)
- **Return structured data** (dicts with `status`, `worker`, `elapsed_seconds`)
- **Log worker hostnames** to debug parallel execution
- **Handle exceptions** and return error dicts instead of raising
- **Time your tasks** (`start_time = time.time()`, then `elapsed = time.time() - start_time`)

#### ❌ DON'T

- **Don't pass Django ORM objects** - pass IDs and re-fetch in the task
- **Don't use global state** - workers are separate processes
- **Don't block workers** - break long tasks into smaller chunks
- **Don't ignore errors** - always log failures with context

### 6) Real-World Example: GADM Pipeline

See `locations/tasks.py` for a production example:

```python
@shared_task(bind=True)
def load_gadm_pipeline(self):
    """
    Full GADM loading pipeline with parallel preprocessing
    
    1. Download GADM data
    2. Clean 'NA' strings (fixes ForeignKey issues)
    3. Preprocess 6 layers in parallel using SedonaDB (5-10x faster)
    4. Load preprocessed layers into PostGIS
    5. Resolve ForeignKey relationships
    """
    # Download & clean
    source_gpkg = download_and_clean_gadm()
    
    # Parallel preprocessing using chord
    workflow = chord(
        group([
            preprocess_gadm_layer_sedonadb.s(i, f'ADM_ADM_{i}', str(source_gpkg))
            for i in range(6)
        ])
    )(load_preprocessed_layers.s())
    
    return workflow.apply_async()
```

This pattern is **reusable for any multi-step ETL pipeline**:
- Download → Clean → Process (parallel) → Load → Resolve

### 7) Learn More

**Official Celery Documentation:**
- [Celery Tasks Guide](https://docs.celeryq.dev/en/stable/userguide/tasks.html) - Task basics, options, best practices
- [Canvas: Workflows](https://docs.celeryq.dev/en/stable/userguide/canvas.html) - `group`, `chain`, `chord` patterns
- [Calling Tasks](https://docs.celeryq.dev/en/stable/userguide/calling.html) - `.delay()`, `.apply_async()`, options
- [Django + Celery](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html) - Integration guide

**Helpful Tutorials:**
- [Real Python: Celery Tasks](https://realpython.com/asynchronous-tasks-with-django-and-celery/) - Practical examples
- [TestDriven.io: Django + Celery](https://testdriven.io/blog/django-and-celery/) - Production patterns

## API Endpoints

- `/locations/places/` - GeoJSON places API
- `/locations/admin_level_0s/` - Country-level admin boundaries
- `/locations/admin_level_1s/` - State/province-level
- `/locations/timezones/` - Timezone data
- `/admin/` - Django admin interface

## Features

### ✅ Complete
- Daphne ASGI server (WSGI + WebSocket support)
- PostGIS spatial database
- Django REST Framework with GIS extensions
- Grappelli enhanced admin interface
- GADM administrative boundaries (global)
- Timezone data
- US Census TIGER data support
- Geocoding via Nominatim
- nginx with static file serving

### 🔄 In Progress
- Synthetic location models refinement
- Additional US Census data integration

### 📋 Planned
- Django Channels (WebSocket support)
- Apache Spark integration
- Apache Sedona (geospatial Spark)
- GeoServer for tile serving
- RabbitMQ for task queue
- Whitenoise for media files

## Makefile Commands

```bash
make build          # Build all Docker images
make up             # Start all services
make down           # Stop all services
make restart        # Restart all services
make logs           # Show logs (add SERVICE=webserver for specific service)
make shell          # Open shell in webserver container
make pg-shell       # Open PostgreSQL shell
make migrate        # Run Django migrations
make collectstatic  # Collect static files
make clean          # Remove containers and volumes
```

## Building

```bash
# First time setup
make build
make up
make migrate
make collectstatic

# Load sample data (optional)
make shell
python hellodjango/manage.py fetch_and_load_standard_spatial_data
python hellodjango/manage.py create_sample_places
```

# References:

- [TestDriven's Django on Docker][1]
- [Runitrupam's Django with Celery/Redis][5]
- [Spark on Docker][6]
- [SSL problem with pip in Docker][7]
- Pip running into SSL problems inside Docker
    - [pip.conf file][8]
    - [where to put pip.conf][9]
- [ARM64 PostGIS Image for Docker][10]
- [Adding Spatialite for dev's SQLite][11]
- [Organizing a settings.py file as a package][12]
- [Django Management Commmand options/arguments][14]
- [Useful Logging template][15]
- [Use Python to generate SHA256 Hash for Files][19]
- [PGDATA variable and path][20]
- [Removing Django migrations to start over][21]
- [Gunicorn Config File][22]
- [Adding a service in Ubuntu][23]
- [Sample Addresses For Testing Geocoder][24]
- [Get field names for a Django Model in the shell][25]
- [Correct healthcheck for PostgreSQL container][26]
- [Sample Data for Locations: Pharmacies in AZ][27]
- [GeoDjango ForeignKeys in LayerMapping][30]
- [CSS FlexBox][31]
- [Check if Django object has attributes][32]
- [GeoDjango get layers from DataSource][33]
- [Geocoding the Pharmacies][34]
- [Get Random Object][35]
- [Django REST Framework Paginator for ListAPIView][36]
- [Django Reset Primary Key for Models][37]
- [Django call management commands from inside Python][38]
- [Reset Django Migrations][39]

[1]: https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/?utm_source=pocket_saves

[2]: https://gunicorn.org

[3]: https://www.nginx.com

[4]: https://www.postgis.net

[5]: https://github.com/runitrupam/Django-Docker-Compose-Celery-Redis-PostgreSQL

[6]: https://medium.com/@SaphE/testing-apache-spark-locally-docker-compose-and-kubernetes-deployment-94d35a54f222

[7]: https://stackoverflow.com/questions/25981703/pip-install-fails-with-connection-error-ssl-certificate-verify-failed-certi/73745221

[8]: https://stackoverflow.com/questions/59287824/specifying-multiple-trusted-hosts-in-pip-conf

[9]: https://stackoverflow.com/questions/38869231/python-cant-find-the-file-pip-conf

[10]: https://github.com/Tob1as/docker-postgresql-postgis

[11]: https://zoomadmin.com/HowToInstall/UbuntuPackage/spatialite-bin

[12]: https://www.reddit.com/r/django/comments/l9s3r4/how_do_you_organize_your_settingspy_file_to_keep/

[13]: https://pub.aimind.so/download-large-file-in-python-with-beautiful-progress-bar-f4f86b394ad7

[14]: https://simpleisbetterthancomplex.com/tutorial/2018/08/27/how-to-create-custom-django-management-commands.html

[15]: https://www.crowdstrike.com/guides/python-logging/logging-with-django/

[16]: https://www.django-rest-framework.org

[17]: https://github.com/openwisp/django-rest-framework-gis

[18]: https://github.com/siege-analytics/socialwarehouse

[19]: https://gist.github.com/jakekara/078899caaf8d5e6c74ef58d16ce7e703

[20]: https://www.postgresql.org/docs/16/storage-file-layout.html

[21]: https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html

[22]: https://stackoverflow.com/questions/12063463/where-is-the-gunicorn-config-file

[23]: https://superuser.com/questions/1839901/how-to-properly-create-a-service-in-ubuntu

[24]:https://github.com/geocommons/geocoder/blob/master/test/data/address-sample.csv

[25]:https://stackoverflow.com/questions/3647805/how-to-get-all-fields-for-a-django-model

[26]:https://github.com/peter-evans/docker-compose-healthcheck/issues/16

[27]:https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://www.azahcccs.gov/Resources/Downloads/PharmacyUpdates/2024/AIHPFee-For-ServicePharmacyNetwork.xlsx&ved=2ahUKEwiUkeX3x8aJAxVxw8kDHVi7EL4QFnoECBEQAQ&usg=AOvVaw1EJLz9kev_tqXZMChl15fj

[28]:https://github.com/nvm-sh/nvm

[29]:https://vite.dev/guide/

[30]:https://stackoverflow.com/questions/21197483/geodjango-layermapping-foreign-key

[31]: https://css-tricks.com/snippets/css/a-guide-to-flexbox/

[32]: https://stackoverflow.com/questions/12906933/how-to-check-if-a-model-object-has-a-given-attribute-property-field-django

[33]: https://gis.stackexchange.com/questions/413084/listing-every-layer-in-geopackage-using-fiona

[34]: https://geocoding.geo.census.gov/geocoder/locations/addressbatch?form

[35]: https://books.agiliq.com/projects/django-orm-cookbook/en/latest/random.html

[36]: https://github.com/AlisherXujanov/Fullstack-Project1/blob/0b7ea1eb103adf49c97287752bae5d1f246fb2f3/DRF.md?plain=1#L834

[37]: https://stackoverflow.com/questions/544791/django-postgresql-how-to-reset-primary-key

[38]: https://docs.djangoproject.com/en/4.0/ref/django-admin/#running-management-commands-from-your-code

[39]: https://medium.com/@mustahibmajgaonkar/how-to-reset-django-migrations-6787b2a1e723