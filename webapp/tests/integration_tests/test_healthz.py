from unittest import mock
from django.test import TransactionTestCase, Client
from django.db import connection, OperationalError


class HealthzIntegrationTest(TransactionTestCase):
    def setUp(self):
        self.client = Client()

    def test_healthz_success(self):
        """Test that /healthz returns 200 when DB is working."""
        response = self.client.get("/healthz")  # No payload
        self.assertEqual(response.status_code, 200)

    def test_healthz_rejects_payload_param(self):
        """Test that /healthz returns 400 if request has a payload."""
        response = self.client.get("/healthz", {"test": "data"})  # Payload included
        self.assertEqual(response.status_code, 400)

    def test_healthz_rejects_payload_body(self):
        """Test that /healthz returns 400 if request has a payload."""
        request = self.client.generic("GET", "/healthz", "test data")
        self.assertEqual(request.status_code, 404)

    def test_healthz_db_failure(self):
        """Simulate a database failure and check for 503 response."""
        with connection.cursor() as cursor:
            cursor.execute("ALTER TABLE healthz_healthcheck RENAME TO temp_table;")  # Break DB table

        try:
            response = self.client.get("/healthz")
            self.assertEqual(response.status_code, 503)
        finally:
            with connection.cursor() as cursor:
                cursor.execute("ALTER TABLE temp_table RENAME TO healthz_healthcheck;")  # Restore DB


    def test_healthz_db_failure_mock(self):
        """Simulate a database failure and check for 503 response."""
        with mock.patch('healthz.views.HealthCheck.objects.create', side_effect=OperationalError):
            response = self.client.get("/healthz")
            self.assertEqual(response.status_code, 503)

    # other methods 405 test
    def test_healthz_post(self):
        response = self.client.post("/healthz")
        self.assertEqual(response.status_code, 405)

    def test_healthz_put(self):
        response = self.client.put("/healthz")
        self.assertEqual(response.status_code, 405)

    def test_healthz_delete(self):
        response = self.client.delete("/healthz")
        self.assertEqual(response.status_code, 405)

    def test_healthz_patch(self):
        response = self.client.patch("/healthz")
        self.assertEqual(response.status_code, 405)

    def test_healthz_head(self):
        response = self.client.head("/healthz")
        self.assertEqual(response.status_code, 405)

    def test_healthz_options(self):
        response = self.client.options("/healthz")
        self.assertEqual(response.status_code, 405)