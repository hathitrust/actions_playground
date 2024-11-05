import unittest
import requests

class TestPythonServer(unittest.TestCase):
    def test_index_htlp_served(self):
        response = requests.get("http://localhost:7000/index.html")
        self.assertEqual(response.status_code, 200)
        self.assertIn("<html>", response.text)

if __name__ == "__main__":
    unittest.main()