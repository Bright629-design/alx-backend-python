#!/usr/bin/env python3
"""
Unit tests for GithubOrgClient class
"""
import unittest
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient"""

    @parameterized.expand([
        ("google", {"login": "google"}),
        ("abc", {"login": "abc"})
    ])
    @patch('client.get_json')
    def test_org(self, org_name, expected, mock_get_json):
        """Test that GithubOrgClient.org returns correct value"""
        mock_get_json.return_value = expected
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        from unittest.mock import patch, PropertyMock

class TestGithubOrgClient(unittest.TestCase):
    # ... previous test methods ...

    def test_public_repos_url(self):
        """Test _public_repos_url returns expected result from mocked org"""
        expected_url = "https://api.github.com/orgs/testorg/repos"

        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock) as mock_org:
            mock_org.return_value = {"repos_url": expected_url}
            client = GithubOrgClient("testorg")
            result = client._public_repos_url
            self.assertEqual(result, expected_url)


from unittest.mock import patch, PropertyMock
import unittest
from parameterized import parameterized
from client import GithubOrgClient

class TestGithubOrgClient(unittest.TestCase):
    # ... previous methods ...

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test public_repos returns expected repo names from payload"""
        mock_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"}
        ]
        mock_get_json.return_value = mock_payload

        expected_repos = ["repo1", "repo2", "repo3"]
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_url:
            mock_url.return_value = "https://api.github.com/orgs/testorg/repos"
            client = GithubOrgClient("testorg")
            result = client.public_repos()

            self.assertEqual(result, expected_repos)
            mock_get_json.assert_called_once()
            mock_url.assert_called_once()


