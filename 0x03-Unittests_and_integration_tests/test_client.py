#!/usr/bin/env python3
"""
Unit and integration tests for GithubOrgClient
"""

import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient, get_json
from fixtures import TEST_PAYLOAD
import requests


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value"""
        expected_payload = {"login": org_name}
        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected_payload)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    @patch("client.GithubOrgClient.org", new_callable=PropertyMock)
    def test_public_repos_url(self, mock_org):
        """Test that _public_repos_url returns the correct URL"""
        payload = {"repos_url": "https://api.github.com/orgs/testorg/repos"}
        mock_org.return_value = payload
        client = GithubOrgClient("testorg")
        self.assertEqual(client._public_repos_url, payload["repos_url"])

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test public_repos returns expected repo names from payload"""
        mock_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"}
        ]
        mock_get_json.return_value = mock_payload
        expected_repos = ["repo1", "repo2", "repo3"]
        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = (
                "https://api.github.com/orgs/testorg/repos"
            )
            client = GithubOrgClient("testorg")
            result = client.public_repos()
            self.assertEqual(result, expected_repos)
            mock_get_json.assert_called_once()
            mock_url.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license correctly evaluates license keys"""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class([
    {
        "org_payload": TEST_PAYLOAD["org_payload"],
        "repos_payload": TEST_PAYLOAD["repos_payload"],
        "expected_repos": TEST_PAYLOAD["expected_repos"],
        "apache2_repos": TEST_PAYLOAD["apache2_repos"],
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests using actual HTTP response payloads"""

    @classmethod
    def setUpClass(cls):
        """Configure patcher for requests.get with fixture payloads"""
        cls.get_patcher = patch("requests.get")
        mock_get = cls.get_patcher.start()

        def side_effect(url):
            if url == TEST_PAYLOAD["org_payload"]["url"]:
                return MockResponse(cls.org_payload)
            elif url == cls.org_payload["repos_url"]:
                return MockResponse(cls.repos_payload)
            return None

        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop patching requests.get"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns expected repos"""
        client = GithubOrgClient("any_org")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos filters by provided license"""
        client = GithubOrgClient("any_org")
        result = client.public_repos(license="apache-2.0")
        self.assertEqual(result, self.apache2_repos)


class MockResponse:
    """Mock response object to simulate requests.get().json()"""

    def __init__(self, json_data):
        self._json_data = json_data

    def json(self):
        return self._json_data
