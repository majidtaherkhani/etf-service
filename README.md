# ETF Analysis Service

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688?style=flat-square&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-316192?style=flat-square&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=flat-square&logo=docker)

A high-performance backend service designed to ingest, manage, and analyze Exchange Traded Fund (ETF) data. This service allows users to upload portfolio compositions and receive real-time historical Net Asset Value (NAV) analysis by cross-referencing user inputs with historical market data.

## 🚀 High-Level Description

The application is built to handle data-intensive operations without compromising user experience. It employs **asynchronous background tasks** to separate high-priority calculation logic from I/O-heavy storage operations.

When a user uploads a CSV:
1.  **Synchronous:** The service immediately calculates the historical NAV and ticker valuations and returns the analysis.
2.  **Asynchronous:** A background process handles the archival of the raw CSV to Object Storage (Firebase) and metadata logging to PostgreSQL.

## 🏗 Architecture & Design

The project follows a **Modular Architecture** with a strict **Layered Design** pattern to ensure separation of concerns and maintainability.

* **Modules:** `storage`, `etf`, `market_data`
* **Layers within modules:**
    * **Routers:** API Interface.
    * **Services:** Business logic and algorithms.
    * **Repositories:** Database interactions.
    * **Schemas (DTOs):** Data validation.
    * **Models:** Define database schemas and ORM relationships.
    * **Exceptions:** Module-specific error handling.

## 🛠 Tech Stack

* **Language:** Python, FastAPI
* **Relational Database:** PostgreSQL (Metadata)
* **Time-Series Database:** TimescaleDB (Historical Market Data)
* **Object Storage:** Firebase / Google Cloud Platform
* **Containerization:** Docker & Docker Compose
* **Migrations:** Alembic
* **Testing:** pytest
* **CI/CD:** GitHub Actions (Deployed to Render)

## ✨ Key Features

* **Portfolio Analysis:** Calculates historical Net Asset Value (NAV) based on weighted ticker prices.
* **Asynchronous Processing:** Non-blocking background tasks for file archival to prevent latency.
* **Rate Limiting:** IP-based throttling to prevent abuse.
* **Data Management:** Polyglot persistence using SQL for structured data and TimescaleDB for time-series data.
* **Robust Error Handling:** Custom exception handlers with descriptive error messages.

## 🔌 API Documentation

### `POST /etf/analyze`

You can try the live API and view the interactive Swagger documentation here:
👉 **[Live API Documentation (Swagger UI)](https://etf-service-th2v.onrender.com/docs)**

* **Input:** Multipart/form-data (CSV file).
* **CSV Requirement:** Must have columns `name` (Ticker) and `weight`.
* **Output:** Historical NAV over time and current ticker valuations.

### `GET /health`
Service health check.

## 📋 Assumptions & Constraints

* **Market Data:** It is assumed that market data prices are pre-populated. For this project, the database is seeded using a seed_db script and a CSV file located in the `sample-data` folder.
* **Ticker Format:** All ticker names in the market data are uppercase.
* **Currency:** All prices are in USD (no currency conversion applied).
* **CSV Format:** Strictly follows `name, weight` headers.

## 💡 Project Philosophy & Design Decisions

**1. Polyglot Persistence (Technical Showcase)**
This project was designed as a demonstration of **backend engineering skills**. I intentionally chose a multi-cloud stack (AWS, GCP, Render) and distinct storage layers (PostgreSQL, TimescaleDB, Firebase).

**2. Raw Data as "Source of Truth"**
The system implements a **Raw Data First** approach. By archiving the original CSV files in Object Storage, we maintain an immutable "Source of Truth." This ensures data integrity and allows for potential re-ingestion or auditing in the future, decoupling the storage layer from the application logic.

## ⚙️ Local Setup & Installation

To run this project locally, you must have **Docker** installed and a PostgreSQL instance with the **TimescaleDB** extension.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/majidtaherkhani/etf-service.git
    cd etf-service
    ```

2.  **Environment Configuration:**
    Create a `.env` file or configure your environment variables:
    * `DATABASE_URL`: Connection string for PostgreSQL (must support TimescaleDB).
    * `FIREBASE_CREDENTIALS`: Path to your Firebase JSON key.

3.  **Run with Docker:**
    ```bash
    docker-compose up --build
    ```

4.  **Run Tests:**
    ```bash
    docker-compose -f docker-compose.test.yml up --build -d
    ```
    ```bash
    docker-compose -f docker-compose.test.yml logs -f
    ```

## ☁️ Deployment

* **App:** Render
* **Database:** AWS
* **Storage:** GCP (Firebase)



