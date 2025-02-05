# from django.test import TestCase
# from django.db import connection
#
# class DatabaseConnectionTest(TestCase):
#     def test_database_connection(self):
#         """Check if Django can connect to MySQL."""
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("SELECT 1;")  # Simple test query
#                 result = cursor.fetchone()
#             self.assertEqual(result[0], 1)
#         except Exception as e:
#             self.fail(f"Database connection failed: {e}")
