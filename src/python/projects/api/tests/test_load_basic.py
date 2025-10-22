"""Basic load test that works with current setup"""

from locust import HttpUser, task, between
import random


class BasicAPIUser(HttpUser):
    """Basic load test user"""
    wait_time = between(1, 3)

    @task(5)
    def health_check(self):
        """Test health endpoint"""
        self.client.get("/healthz")

    @task(2)
    def readiness_check(self):
        """Test readiness endpoint"""
        self.client.get("/readyz")

    @task(1)
    def root_endpoint(self):
        """Test root endpoint"""
        self.client.get("/")

    @task(1)
    def docs_endpoint(self):
        """Test docs endpoint"""
        self.client.get("/docs")

    @task(1)
    def openapi_endpoint(self):
        """Test OpenAPI spec"""
        self.client.get("/openapi.json")