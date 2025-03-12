📦 my_api/
 ┣ 📂 app/
 ┃ ┣ 📂 routers/            # Contains the API endpoints
 ┃ ┃ ┣ 📜 users.py
 ┃ ┃ ┣ 📜 products.py
 ┃ ┃ ┣ 📜 spaces.py
 ┃ ┃ ┣ 📜 styles.py
 ┃ ┃ ┗ 📜 __init__.py
 ┃ ┣ 📂 models/             # Database models (SQLAlchemy)
 ┃ ┃ ┣ 📜 users.py
 ┃ ┃ ┣ 📜 products.py
 ┃ ┃ ┣ 📜 spaces.py
 ┃ ┃ ┣ 📜 styles.py
 ┃ ┃ ┗ 📜 __init__.py
 ┃ ┣ 📂 schemas/            # Pydantic schemas for data validation
 ┃ ┃ ┣ 📜 users.py
 ┃ ┃ ┣ 📜 products.py
 ┃ ┃ ┣ 📜 spaces.py
 ┃ ┃ ┣ 📜 styles.py
 ┃ ┃ ┗ 📜 __init__.py
 ┃ ┣ 📂 services/           # Business logic for each entity
 ┃ ┃ ┣ 📜 users.py
 ┃ ┃ ┣ 📜 products.py
 ┃ ┃ ┣ 📜 spaces.py
 ┃ ┃ ┣ 📜 styles.py
 ┃ ┃ ┗ 📜 __init__.py
 ┃ ┣ 📂 core/               # Global configurations
 ┃ ┃ ┣ 📜 database.py       # Database connection
 ┃ ┃ ┣ 📜 config.py         # Environment variables
 ┃ ┃ ┗ 📜 __init__.py
 ┃ ┣ 📂 dependencies/       # Reusable dependencies (Auth, DB, etc.)
 ┃ ┃ ┣ 📜 auth.py
 ┃ ┃ ┣ 📜 db.py
 ┃ ┃ ┗ 📜 __init__.py
 ┃ ┣ 📜 main.py             # Entry point of the application
 ┃ ┗ 📜 __init__.py
 ┣ 📜 .env                  # Environment variables
┣ 📜 requirements.txt       # Project dependencies
┣ 📜 README.md              # Project documentation