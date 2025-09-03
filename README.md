# Splitwise Backend

A backend service for managing group expenses, settlements, and user balances, inspired by the functionality of Splitwise. This system allows users to create groups, add members, track shared expenses, calculate balances, and settle up debts within groups.

## Features
- **Groups**: Create groups, add/remove members, and manage group membership.
- **Expenses**: Add, update, and remove expenses for a group. Split expenses among members and track individual shares.
- **Settlements**: Settle debts, view settlement history, and calculate optimal settlements to minimize transactions.
- **Users**: Manage user accounts, including registration, authentication, and user retrieval.

## Technologies Used

- **Python 3.12**
- **SQLAlchemy**
- **FastAPI**
- **PostgreSQL**
- **Alembic**

## Getting Started

### Prerequisites

- Python 3.12
- PostgreSQL

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vin0dkhichar/splitwise-backend.git
   cd splitwise-backend
   ```

2. **Set up a virtual environment with Python 3.12:**
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory with the following content:
   ```
   DATABASE_URL=postgresql+psycopg2://postgres:admin@localhost:5432/splitwise
   SECRET_KEY=your-super-secret-key-here-make-it-long-and-complex
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```

5. **Database Setup:**
   ```bash
   # Create database
   createdb -U postgres splitwise
   
   # Initialize Alembic
   alembic init migrations
   
   # Configure alembic.ini with your DATABASE_URL
   # Update alembic/env.py to import your models
   
   # Generate and run migrations
   alembic revision --autogenerate -m "Initial tables"
   alembic upgrade head
   ```

6. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000` and the interactive documentation at `http://localhost:8000/docs`.
