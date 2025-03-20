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

cd webapp # Go to webapp
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

## **Testing**

### **Run tests**
```bash
python manage.py test
```

## Packer Summary

Packer is used to create machine images for deployment. The configuration is defined in a Packer template file (`setup.pkr.hcl`), which includes the necessary builders and provisioners.

### Steps to Run Packer

1. **Install Packer**
    - Download and install Packer from the [official website](https://www.packer.io/downloads).


2. **Navigate to the Packer Directory**
   ```bash
   cd webapp/packer_setup
   ```

3. **Validate the Packer Template**
   ```bash
   packer validate setup.pkr.hcl
   ```

4. **Build the Image**
   ```bash
   packer build setup.pkr.hcl
   ```

Ensure your AWS credentials are properly configured before running the Packer commands.


## GitHub Actions
**GitHub Actions** to automate Continuous Integration (CI) and infrastructure provisioning with **Packer**. The workflows ensure code quality, database migrations, and infrastructure setup are handled efficiently.

## Workflows

### **Django CI**
This workflow is triggered on every pull request to the `main` branch. It performs the following tasks:

- **Repository Checkout:** Pulls the latest code changes.
- **Python Setup:** Configures the required Python version.
- **Database Initialization:** Starts MySQL and creates the necessary database.
- **Dependency Installation:** Installs required Python dependencies.
- **Migrations & Testing:** Runs database migrations and executes Django test cases to ensure application stability.

### **Packer Setup**
This workflow is triggered on pull requests to `main` and validates the Packer template before building infrastructure. The key steps include:

- **Repository Checkout:** Fetches the latest code.
- **Artifact Preparation:** Zips necessary files and uploads them as a build artifact.
- **Packer Initialization:** Sets up Packer and ensures configurations follow the correct format.
- **Template Validation:** Runs validation checks to confirm that the Packer template is correctly configured.

### **Packer Build**
Triggered after a pull request is merged into `main`, this workflow automates the Packer image creation process. The steps include:

- **Python Setup & Testing:** Similar to Django CI, ensuring all tests pass before proceeding.
- **AWS Configuration:** Configures AWS credentials for AMI creation.
- **Build Artifact Handling:** Downloads the previously created artifact.
- **Packer Image Creation:** Builds the infrastructure image using predefined Packer configurations.

## Environment Variables & Secrets
The workflows rely on **GitHub Secrets** to manage sensitive configurations securely, including database credentials, AWS access keys, and Django secret keys.

## Notes
- Values for variables should not be hardcoded; they must be configurable for demonstration purposes.
- The RDS instance should be private and accessible only from authorized sources.
- The S3 bucket must be **private, encrypted, and include a lifecycle policy** for storage optimization.

## S3 Image Upload

This application now supports uploading images to Amazon S3. Below are the details of the new endpoints and their functionalities:

### Endpoints

- **Upload Image**
    - **URL:** `/v1/file`
    - **Method:** `POST`
    - **Description:** Uploads an image to S3 and stores the image metadata in the database.
    - **Request:**
        - **Form Data:** `profilePic` (file)
    - **Response:**
      ```json
      {
        "file_name": "example.jpg",
        "id": "unique-image-id",
        "url": "https://your-bucket-name.s3.amazonaws.com/unique-image-id/example.jpg",
        "upload_date": "YYYY-MM-DD",
        "image_type": "image/jpeg"
      }
      ```

- **Get Image**
    - **URL:** `/v1/file/<image_id>`
    - **Method:** `GET`
    - **Description:** Retrieves the image metadata from the database.
    - **Response:**
      ```json
      {
        "file_name": "example.jpg",
        "id": "unique-image-id",
        "url": "https://your-bucket-name.s3.amazonaws.com/unique-image-id/example.jpg",
        "upload_date": "YYYY-MM-DD"
      }
      ```

- **Delete Image**
    - **URL:** `/v1/file/<image_id>`
    - **Method:** `DELETE`
    - **Description:** Deletes the image from S3 and removes the metadata from the database.
    - **Response:** `204 No Content`

### Configuration

Ensure the following environment variables are set in your `.env` file:

- `S3_BUCKET_NAME`: The name of your S3 bucket.

### Setup

1. Create a new Linux group and user for the application.
2. Create the necessary directories and set permissions.
3. Create and activate a virtual environment.
4. Install the required packages.
5. Move the service file to `/etc/systemd/system` and start the server.

Refer to the `webapp/scripts/webapp_setup.sh` script for detailed setup instructions.




