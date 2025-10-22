"""
Stress testing scenarios for PWC Contract Analysis API

This script provides pre-configured stress test scenarios
for different load patterns.
"""

from locust import HttpUser, task, between, constant
import json
import random
import io


class HighVolumeUploadUser(HttpUser):
    """
    Stress test focused on high-volume contract uploads
    """
    wait_time = constant(1)  # Constant 1 second wait for stress testing

    def on_start(self):
        """Setup for high volume testing"""
        self.auth_token = None
        self.user_id = f"stress_user_{random.randint(10000, 99999)}"
        self.client_id = None
        self.setup_user()

    def setup_user(self):
        """Quick user setup for stress testing"""
        # Register
        user_data = {
            "username": self.user_id,
            "email": f"{self.user_id}@stresstest.com",
            "password": "StressTest123!"
        }

        self.client.post("/api/v1/auth/register", json=user_data)

        # Login
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }

        response = self.client.post("/api/v1/auth/login", data=login_data)
        if response.status_code == 200:
            self.auth_token = response.json()["access_token"]

        # Create client
        if self.auth_token:
            client_data = {
                "name": f"Stress Client {self.user_id}",
                "company": "Stress Test Corp"
            }
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.client.post("/api/v1/clients/", json=client_data, headers=headers)
            if response.status_code == 200:
                self.client_id = response.json()["id"]

    def get_stress_pdf_content(self):
        """Generate PDF content for stress testing"""
        size_kb = random.randint(10, 100)  # Random size between 10-100KB
        content = b"%PDF-1.4\n" + b"X" * (size_kb * 1024 - 10) + b"\n%%EOF"
        return content

    @task(10)
    def rapid_contract_upload(self):
        """Rapid contract uploads for stress testing"""
        if not self.auth_token or not self.client_id:
            return

        pdf_content = self.get_stress_pdf_content()
        filename = f"stress_contract_{random.randint(100000, 999999)}.pdf"

        files = {
            "file": (filename, io.BytesIO(pdf_content), "application/pdf")
        }
        data = {
            "client_id": self.client_id
        }
        headers = {"Authorization": f"Bearer {self.auth_token}"}

        self.client.post("/api/v1/contracts/", files=files, data=data, headers=headers)


class ConcurrentAnalysisUser(HttpUser):
    """
    Stress test focused on concurrent analysis requests
    """
    wait_time = between(0.5, 1.5)

    def on_start(self):
        """Setup for concurrent analysis testing"""
        self.auth_token = None
        self.user_id = f"analysis_user_{random.randint(10000, 99999)}"
        self.setup_user()

    def setup_user(self):
        """Setup user for analysis stress testing"""
        user_data = {
            "username": self.user_id,
            "email": f"{self.user_id}@analysistest.com",
            "password": "AnalysisTest123!"
        }

        self.client.post("/api/v1/auth/register", json=user_data)

        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }

        response = self.client.post("/api/v1/auth/login", data=login_data)
        if response.status_code == 200:
            self.auth_token = response.json()["access_token"]

    def get_analysis_pdf_content(self):
        """Generate PDF with contract-like content for analysis"""
        contract_text = f"""
        CONTRACT AGREEMENT {random.randint(1000, 9999)}

        PARTIES:
        - Company A (Client)
        - Company B (Service Provider)

        PAYMENT TERMS:
        Payment shall be made within {random.choice([15, 30, 45, 60])} days of invoice receipt.

        TERMINATION:
        Either party may terminate this agreement with {random.choice([7, 14, 30])} days written notice.

        LIABILITY:
        Total liability shall not exceed ${random.randint(10000, 100000):,}.

        GOVERNING LAW:
        This agreement shall be governed by the laws of {random.choice(['California', 'New York', 'Texas'])}.
        """

        pdf_content = f"""%PDF-1.4
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
/Length {len(contract_text)}
>>
stream
BT
/F1 10 Tf
50 750 Td
{contract_text}
Tj
ET
endstream
endobj

trailer
<<
/Size 5
/Root 1 0 R
>>
%%EOF""".encode()

        return pdf_content

    @task(8)
    def concurrent_direct_analysis(self):
        """Concurrent direct analysis requests"""
        if not self.auth_token:
            return

        pdf_content = self.get_analysis_pdf_content()
        filename = f"analysis_stress_{random.randint(100000, 999999)}.pdf"

        files = {
            "file": (filename, io.BytesIO(pdf_content), "application/pdf")
        }
        headers = {"Authorization": f"Bearer {self.auth_token}"}

        self.client.post("/api/v1/genai/analyze-contract", files=files, headers=headers)

    @task(2)
    def evaluation_stress(self):
        """Stress test evaluation with direct clauses"""
        if not self.auth_token:
            return

        clauses_data = {
            "clauses": [
                {
                    "type": "payment_terms",
                    "content": f"Payment within {random.choice([15, 30, 45, 60])} days",
                    "confidence": random.uniform(0.8, 0.99)
                },
                {
                    "type": "termination",
                    "content": f"Termination with {random.choice([7, 14, 30])} days notice",
                    "confidence": random.uniform(0.8, 0.99)
                },
                {
                    "type": "liability",
                    "content": f"Liability cap of ${random.randint(10000, 100000):,}",
                    "confidence": random.uniform(0.8, 0.99)
                }
            ]
        }

        headers = {"Authorization": f"Bearer {self.auth_token}"}
        self.client.post("/api/v1/genai/evaluate-clauses", json=clauses_data, headers=headers)


class DatabaseStressUser(HttpUser):
    """
    Stress test focused on database operations
    """
    wait_time = constant(0.5)

    def on_start(self):
        """Setup for database stress testing"""
        self.auth_token = None
        self.user_id = f"db_user_{random.randint(10000, 99999)}"
        self.setup_user()

    def setup_user(self):
        """Setup user for database stress testing"""
        user_data = {
            "username": self.user_id,
            "email": f"{self.user_id}@dbtest.com",
            "password": "DbTest123!"
        }

        self.client.post("/api/v1/auth/register", json=user_data)

        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }

        response = self.client.post("/api/v1/auth/login", data=login_data)
        if response.status_code == 200:
            self.auth_token = response.json()["access_token"]

    @task(15)
    def rapid_list_requests(self):
        """Rapid listing requests to stress database"""
        if not self.auth_token:
            return

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        endpoints = [
            "/api/v1/contracts/",
            "/api/v1/clients/",
            "/api/v1/logs",
            "/api/v1/metrics"
        ]

        endpoint = random.choice(endpoints)
        self.client.get(endpoint, headers=headers)

    @task(5)
    def pagination_stress(self):
        """Stress test pagination"""
        if not self.auth_token:
            return

        headers = {"Authorization": f"Bearer {self.auth_token}"}
        params = {
            "skip": random.randint(0, 100),
            "limit": random.randint(10, 100)
        }

        self.client.get("/api/v1/contracts/", params=params, headers=headers)


# Load distribution for stress testing
HighVolumeUploadUser.weight = 3
ConcurrentAnalysisUser.weight = 4
DatabaseStressUser.weight = 3