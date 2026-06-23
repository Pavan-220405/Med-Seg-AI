# Med-Seg-AI

A FastAPI backend for **medical image segmentation**, built around a U-Net deep-learning model for **brain tumor segmentation**. It exposes a secure, token-authenticated REST API for running inference on MRI scans, managing a registry of ML models, and tracking prediction history.

The service loads a trained Keras/TensorFlow U-Net at startup, accepts an uploaded scan, returns the original image with the predicted tumor region overlaid, and persists both the input and the generated mask along with inference metadata.

---

## Features

- **Brain tumor segmentation** — upload a brain MRI image and receive a PNG with the predicted tumor mask overlaid in red.
- **JWT authentication** — access/refresh token flow with token-type validation, expiry, and refresh-token revocation (logout) backed by a Redis blocklist.
- **Role-based access control** — `user`, `radiologist`, and `admin` roles; admin-only operations are guarded by a role checker.
- **Model registry** — admins can register and remove ML models, each with version, framework, type, storage path, and evaluation metrics.
- **Prediction tracking** — every inference is recorded in the database with the input/mask paths and measured inference time.
- **Async stack** — `asyncpg` connection pooling for PostgreSQL and `redis.asyncio` for the token blocklist, managed through the FastAPI lifespan.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API framework | FastAPI + Uvicorn |
| ML runtime | TensorFlow 2.11 / Keras 2.11 (U-Net, `.h5` model) |
| Image processing | OpenCV, NumPy |
| Database | PostgreSQL (via `asyncpg`) |
| Cache / token store | Redis (via `redis.asyncio`) |
| Migrations | Alembic |
| Auth | PyJWT, bcrypt, passlib |
| Config | Pydantic `BaseSettings` (`.env`) |

---

## Project Structure

```
.
├── app/
│   ├── main.py                  # FastAPI app, lifespan startup/shutdown, router registration
│   ├── config.py                # Pydantic settings loaded from .env
│   ├── db/
│   │   ├── engine.py            # asyncpg connection pool (init/get/close)
│   │   └── redis_engine.py      # Redis client + JWT blocklist helpers
│   ├── auth/
│   │   ├── utils.py             # password hashing, JWT create/decode
│   │   └── dependencies.py      # token bearers, get_conn, current-user & role-checker deps
│   ├── users/
│   │   ├── routes.py            # signup, login, refresh, logout, make_admin
│   │   ├── crud.py              # user DB operations
│   │   └── schemas.py           # user Pydantic models
│   └── ML_models/
│       ├── routes.py            # model registry endpoints (add/delete)
│       ├── crud.py              # model & prediction DB operations
│       ├── schemas.py           # model & prediction Pydantic models
│       ├── Brain_Tumor_Segmentation/
│       │   ├── routes.py        # /predict inference endpoint
│       │   ├── utils.py         # model lifecycle, file validation, preprocessing
│       │   ├── best_model.h5    # trained U-Net weights (not committed — see below)
│       │   └── *.ipynb          # training / testing notebooks
│       └── Brain_Tumor_Classification/   # placeholder for a future classification model
├── alembic/                     # database migrations
├── alembic.ini
├── requirements.txt             # core dependency list
├── final_requirements.txt       # full pinned dependency set (incl. transitive)
└── Notes/                       # background reading (U-Net / CNN PDFs)
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL (a database named `MedSegAI` by default)
- Redis
- The trained model weights file `best_model.h5` placed in
  `app/ML_models/Brain_Tumor_Segmentation/` (model weights are git-ignored and must be supplied separately).

### 1. Install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# or, for the fully pinned environment:
# pip install -r final_requirements.txt
```

### 2. Configure environment

Create a `.env` file in the project root:

```env
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRY_MINUTES=15
REFRESH_TOKEN_EXPIRY_DAYS=7
DATABASE_URL=postgresql://postgres:1234@localhost:5432/MedSegAI
REDIS_HOST=localhost
REDIS_PORT=6379
JTI_EXPIRY=60
```

> `REDIS_HOST`, `REDIS_PORT`, and `JTI_EXPIRY` have defaults (`localhost`, `6379`, `60`) and can be omitted.

### 3. Run database migrations

The migration connection string lives in `alembic.ini` (`sqlalchemy.url`) — update it to match your database before running:

```bash
alembic upgrade head
```

### 4. Start the server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs are served at `http://localhost:8000/docs`.

---

## API Reference

All routes are prefixed with `/api/v1`. Protected routes require an `Authorization: Bearer <token>` header.

### Users — `/api/v1/users`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/signup` | Public | Register a new user (`user` or `radiologist`). |
| POST | `/login` | Public | Authenticate; returns access + refresh tokens and user details. |
| POST | `/refresh_token` | Refresh token | Issue a new access token. |
| POST | `/logout` | Refresh token | Revoke the refresh token (adds its `jti` to the Redis blocklist). |
| POST | `/make_admin` | Admin | Promote a user to `admin` by email. |
| GET | `/` | Access token | List active models. |

### Segmentation — `/api/v1/segmentation`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/predict` | Access token | Upload a brain MRI image; returns a PNG with the tumor mask overlaid. Saves input/mask and records the prediction. |

Accepted upload formats: `.png`, `.tif`, `.tiff`. Images are resized to 256×256 and normalized before inference; the mask is thresholded at 0.5.

### Models — `/api/v1/models`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/` | Admin | Register a new model in the registry. |
| DELETE | `/{model_id}` | Admin | Remove a model by UUID. |

---

## Database Schema

Managed by Alembic migrations under `alembic/versions/`.

- **users** — `id`, `user_name`, `first_name`, `last_name`, `email`, `hashed_password`, `role` (`user` / `radiologist` / `admin` / `expert`), `joined_at`.
- **models** — `id`, `model_name`, `version`, `description`, `framework`, `model_type`, `model_path`, `metrics` (JSONB), `is_active`, `created_at`, `added_by` → `users(id)`. Unique on `(model_name, version)`.
- **predictions** — `prediction_id`, `user_id` → `users(id)`, `model_id` → `models(id)`, `input_path`, `mask_path`, `inference_time`, `created_at`.

---

## How Inference Works

1. The U-Net model (`best_model.h5`) is loaded once at application startup via the FastAPI lifespan (`init_model`) and held in memory.
2. On `POST /predict`, the uploaded file's extension and contents are validated, then decoded with OpenCV.
3. The image is converted to RGB, resized to 256×256, and normalized to `[0, 1]`.
4. The model predicts a mask; values above `0.5` are kept as the tumor region.
5. The mask is overlaid in red (alpha 0.55) on the original image and returned as a PNG.
6. The input image and generated mask are written to `segmentation_storage/`, and a prediction record is persisted to the database with the measured inference time.

> The segmentation `MODEL_ID` is currently hard-coded in `Brain_Tumor_Segmentation/routes.py`; this can be made dynamic once a full model registry/selection flow is in place.

---

## Notes

- Model weight files (`*.h5`, `*.pt`, `*.pth`, `*.ckpt`, `*.pkl`) and the `segmentation_storage/` directory are git-ignored.
- The `Brain_Tumor_Classification/` module is a placeholder for a future classification model.
- Training and testing experiments are kept in the Jupyter notebooks under `Brain_Tumor_Segmentation/`.
