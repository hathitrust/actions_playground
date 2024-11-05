import unittest
import requests
import threading
import time
from server import run_server

class TestPythonServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_thread = threading.Thread(target=run_server)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(1)
    def test_index_htlp_served(self):
        response = requests.get("http://localhost:7000/index.html")
        self.assertEqual(response.status_code, 200)
        self.assertIn("<html>", response.text)

if __name__ == "__main__":
    unittest.main()