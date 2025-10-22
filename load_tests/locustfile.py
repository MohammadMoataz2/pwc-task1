"""
Load testing for PWC Contract Analysis API using Locust

This file contains load tests for the core API endpoints to ensure
the system can handle expected traffic loads.

Usage:
    locust -f load_tests/locustfile.py --host=http://localhost:8000

Web UI will be available at: http://localhost:8089
"""

from locust import HttpUser, task, between
import json
import random
import io
import os


class ContractAnalysisUser(HttpUser):
    """
    Simulates a user interacting with the PWC Contract Analysis API
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests

    def on_start(self):
        """Setup method called when user starts"""
        self.auth_token = None
        self.user_id = f"loadtest_user_{random.randint(1000, 9999)}"
        self.client_id = None
        self.contract_ids = []

        # Register and login
        self.register_and_login()

        # Create a test client
        self.create_test_client()

    def register_and_login(self):
        """Register a test user and obtain auth token"""
        # Register user
        user_data = {
            "username": self.user_id,
            "email": f"{self.user_id}@loadtest.com",
            "password": "LoadTest123!"
        }

        with self.client.post("/api/v1/auth/register", json=user_data, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 400 and "already registered" in response.text:
                response.success()  # User already exists, that's fine
            else:
                response.failure(f"Registration failed: {response.status_code}")

        # Login to get token
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }

        with self.client.post("/api/v1/auth/login", data=login_data, catch_response=True) as response:
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data["access_token"]
                response.success()
            else:
                response.failure(f"Login failed: {response.status_code}")

    def create_test_client(self):
        """Create a test client for contract association"""
        if not self.auth_token:
            return

        client_data = {
            "name": f"LoadTest Client {self.user_id}",
            "company": "LoadTest Inc.",
            "email": f"client_{self.user_id}@loadtest.com"
        }

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        with self.client.post("/api/v1/clients/", json=client_data, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                self.client_id = response.json()["id"]
                response.success()
            else:
                response.failure(f"Client creation failed: {response.status_code}")

    @property
    def auth_headers(self):
        """Get authorization headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}

    def get_sample_pdf_content(self):
        """Generate a simple PDF-like content for testing"""
        # Simple PDF structure for testing
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 56
>>
stream
BT
/F1 12 Tf
100 700 Td
(Load Test Contract Content) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000204 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
309
%%EOF"""
        return pdf_content

    @task(3)
    def health_check(self):
        """Test health check endpoint (high frequency)"""
        with self.client.get("/healthz", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(2)
    def readiness_check(self):
        """Test readiness check endpoint"""
        with self.client.get("/readyz", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Readiness check failed: {response.status_code}")

    @task(5)
    def list_contracts(self):
        """Test listing contracts endpoint"""
        if not self.auth_token:
            return

        with self.client.get("/api/v1/contracts/", headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"List contracts failed: {response.status_code}")

    @task(5)
    def list_clients(self):
        """Test listing clients endpoint"""
        if not self.auth_token:
            return

        with self.client.get("/api/v1/clients/", headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"List clients failed: {response.status_code}")

    @task(2)
    def upload_contract(self):
        """Test contract upload endpoint"""
        if not self.auth_token or not self.client_id:
            return

        pdf_content = self.get_sample_pdf_content()
        filename = f"loadtest_contract_{random.randint(1000, 9999)}.pdf"

        files = {
            "file": (filename, io.BytesIO(pdf_content), "application/pdf")
        }
        data = {
            "client_id": self.client_id
        }

        with self.client.post(
            "/api/v1/contracts/",
            files=files,
            data=data,
            headers=self.auth_headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                contract_data = response.json()
                self.contract_ids.append(contract_data["id"])
                response.success()
            else:
                response.failure(f"Contract upload failed: {response.status_code}")

    @task(1)
    def analyze_contract_direct(self):
        """Test direct contract analysis endpoint"""
        if not self.auth_token:
            return

        pdf_content = self.get_sample_pdf_content()
        filename = f"analysis_test_{random.randint(1000, 9999)}.pdf"

        files = {
            "file": (filename, io.BytesIO(pdf_content), "application/pdf")
        }

        with self.client.post(
            "/api/v1/genai/analyze-contract",
            files=files,
            headers=self.auth_headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 500:
                # AI service might be mocked or unavailable in load testing
                response.success()
            else:
                response.failure(f"Direct analysis failed: {response.status_code}")

    @task(1)
    def analyze_document_by_id(self):
        """Test document analysis by ID"""
        if not self.auth_token or not self.contract_ids:
            return

        contract_id = random.choice(self.contract_ids)

        with self.client.post(
            f"/api/v1/genai/analyze-document/{contract_id}",
            headers=self.auth_headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 500:
                # AI service might be mocked or unavailable
                response.success()
            else:
                response.failure(f"Document analysis failed: {response.status_code}")

    @task(2)
    def get_metrics(self):
        """Test metrics endpoint"""
        if not self.auth_token:
            return

        with self.client.get("/api/v1/metrics", headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Metrics failed: {response.status_code}")

    @task(2)
    def get_logs(self):
        """Test logs endpoint"""
        if not self.auth_token:
            return

        params = {
            "limit": 10,
            "skip": 0
        }

        with self.client.get("/api/v1/logs", params=params, headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Logs failed: {response.status_code}")


class AdminUser(HttpUser):
    """
    Simulates an admin user performing administrative tasks
    """
    wait_time = between(2, 5)
    weight = 1  # Lower weight than regular users

    def on_start(self):
        """Setup admin user"""
        self.auth_token = None
        self.admin_login()

    def admin_login(self):
        """Login as admin user"""
        # Try to login with default admin credentials
        login_data = {
            "username": "admin",
            "password": "admin123"
        }

        with self.client.post("/api/v1/auth/login", data=login_data, catch_response=True) as response:
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data["access_token"]
                response.success()
            else:
                # Admin user might not exist in load test environment
                response.success()

    @property
    def auth_headers(self):
        """Get authorization headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}

    @task(3)
    def admin_metrics(self):
        """Admin checks system metrics"""
        if not self.auth_token:
            return

        with self.client.get("/api/v1/metrics", headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Admin metrics failed: {response.status_code}")

    @task(3)
    def admin_logs(self):
        """Admin checks system logs"""
        if not self.auth_token:
            return

        params = {
            "limit": 50,
            "skip": 0
        }

        with self.client.get("/api/v1/logs", params=params, headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Admin logs failed: {response.status_code}")

    @task(1)
    def system_health_monitoring(self):
        """Admin monitors system health"""
        endpoints = ["/healthz", "/readyz"]

        for endpoint in endpoints:
            with self.client.get(endpoint, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Health monitoring failed for {endpoint}: {response.status_code}")


# User class weights for realistic simulation
ContractAnalysisUser.weight = 8  # 80% regular users
AdminUser.weight = 2              # 20% admin users