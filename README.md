# Web Application - Health Check API

## Overview
This is a cloud-native backend web application built using **Django** and **MySQL**.  
It implements a **health check API (`/healthz`)** that records application status and ensures smooth operation.

## Features
- Uses **Python Django** as the backend framework.
- Stores health check logs in a **MySQL database**.
- Implements **RESTful API** following cloud-native requirements.
- Supports only **HTTP GET** requests.
- Returns **HTTP status codes** based on request validity and database availability.
- Follows **MVC architecture** with an `.env` file for security.

---

## **Prerequisites**
Before setting up the project, ensure you have:
- Python **3.9+**
- MySQL **8.0+**
- Pip (Python package manager)
- Virtual environment support
- `curl` or **Postman** for testing API requests
- **GitHub account** for repository management

---

## **Installation & Setup**

### **1. Clone the Repository**
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/webapp.git
cd webapp
```

### **2. Create a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Set Up Environment Variables**
Create a .env file in the project root and add:
```makefile
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
SECRET_KEY=your_django_secret_key
```

### **5. Configure Database**
Start MySQL and create a database manually:
```sql
CREATE DATABASE your_database_name;
```

Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### **6. Run the Server**
```bash
python manage.py runserver
```







