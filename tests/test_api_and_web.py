from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "TechChallengeVF"))

from json_api_server import create_app  # noqa: E402


class TechChallengeApiTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(use_db=False)
        self.client = self.app.test_client()

    def test_health_dashboard_and_sample_endpoints(self):
        r = self.client.get("/api/health")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json()["ok"])

        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        self.assertIn(b"Modern Dashboard", home.data)

        results = self.client.get("/data/results.json")
        self.assertEqual(results.status_code, 200)
        self.assertEqual(results.headers.get("X-Data-Source"), "sample")
        self.assertIsInstance(results.get_json(), list)

        files = self.client.get("/data/files.json")
        self.assertEqual(files.status_code, 200)
        self.assertIsInstance(files.get_json(), list)

        events = self.client.get("/data/events.json")
        self.assertEqual(events.status_code, 200)
        self.assertIsInstance(events.get_json(), list)


if __name__ == "__main__":
    unittest.main()
