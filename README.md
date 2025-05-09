# Broker Platform

A Flask-based broker platform with investment packages, user dashboard, and admin panel.

## Features

- User registration and authentication
- Investment packages with ROI calculation
- Wallet system for deposits and withdrawals
- Admin panel for managing users, packages, and investments
- Trading charts and data visualization
- Responsive design with Tailwind CSS

## Prerequisites

- Python 3.8+
- Node.js and npm (for Tailwind CSS)
- SQLite (default) or any other database supported by SQLAlchemy

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd broker_platform
```

### 2. Create and activate a virtual environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and build Tailwind CSS

```bash
npm install
npx tailwindcss -i ./src/input.css -o ./app/static/css/styles.css
```

### 5. Initialize the database

```bash
python init_app.py
```

### 6. Run the application

```bash
python run.py
```

The application will be available at http://127.0.0.1:5000/

## Default Login Credentials

### Admin
- Username: admin
- Password: admin1234

### Test User
- Username: testuser
- Password: user1234

## Project Structure

```
broker_platform/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── auth.py
│   │   └── user.py
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── js/
│   │   │   └── app.js
│   │   └── img/
│   ├── templates/
│   │   ├── admin/
│   │   ├── auth/
│   │   ├── user/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── about.html
│   │   └── contact.html
│   ├── forms.py
│   └── utils.py
│
├── instance/
│   └── broker.db
│
├── migrations/
│
├── config.py
├── run.py
├── init_app.py
├── requirements.txt
└── tailwind.config.js
```

## Development

### Watching Tailwind CSS changes

```bash
npx tailwindcss -i ./src/input.css -o ./app/static/css/styles.css --watch
```

### Database Migrations

If you make changes to the database models:

```bash
flask db init    # Only run once to initialize migrations
flask db migrate -m "Description of changes"
flask db upgrade
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Chart.js](https://www.chartjs.org/)



10. Log in with default credentials
Admin Panel

URL: http://127.0.0.1:5000/admin/dashboard
Username: admin
Password: admin1234

User Account

URL: http://127.0.0.1:5000/login
Username: testuser
Password: user1234#   t r a d i n g c l o n e  
 