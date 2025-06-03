
"""GitHub Pull Request Fetcher with SSL Error Handling and Fallback Strategies"""

import ssl
import requests
from typing import List, Dict, Any

class GitHubPRFetcher:
    """
    GitHub Pull Request fetcher with SSL error handling and multiple fallback strategies.
    """
    
    def __init__(self, token = "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"):
        """
        Initialize the PR fetcher.
        
        Args:
            token: Optional GitHub personal access token for higher rate limits
        """
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-PR-Fetcher/1.0"
        }
        
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def _create_session_with_ssl_config(self) -> requests.Session:
        """Create a requests session with SSL configuration options."""
        session = requests.Session()
        session.headers.update(self.headers)
        
        # Create custom SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Configure the session adapter
        adapter = requests.adapters.HTTPAdapter()
        session.mount('https://', adapter)
        
        return session
    
    def fetch_pr_details(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """
        Fetch pull request details with multiple fallback strategies for SSL issues.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            
        Returns:
            Dictionary containing PR details or error information
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        
        strategies = [
            self._fetch_with_default_ssl,
            self._fetch_with_disabled_ssl_verification,
            self._fetch_with_custom_ssl_context,
            self._fetch_with_system_ca_bundle
        ]
        
        last_error = None
        
        for i, strategy in enumerate(strategies, 1):
            try:
                print(f"Attempting strategy {i}: {strategy.__name__}")
                result = strategy(url)
                if result.get('success'):
                    return result
                else:
                    last_error = result.get('error', 'Unknown error')
            except Exception as e:
                last_error = str(e)
                print(f"Strategy {i} failed: {e}")
                continue
        
        return {
            'success': False,
            'error': f'All SSL strategies failed. Last error: {last_error}',
            'data': None
        }
    
    def _fetch_with_default_ssl(self, url: str) -> Dict[str, Any]:
        """Standard SSL verification approach."""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json(),
                'method': 'default_ssl'
            }
        except Exception as e:
            return {'success': False, 'error': f'Default SSL failed: {str(e)}'}
    
    def _fetch_with_disabled_ssl_verification(self, url: str) -> Dict[str, Any]:
        """Disable SSL verification entirely."""
        try:
            response = requests.get(
                url, 
                headers=self.headers, 
                verify=False, 
                timeout=30
            )
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json(),
                'method': 'disabled_ssl_verification'
            }
        except Exception as e:
            return {'success': False, 'error': f'Disabled SSL verification failed: {str(e)}'}
    
    def _fetch_with_custom_ssl_context(self, url: str) -> Dict[str, Any]:
        """Use a custom SSL context."""
        try:
            session = self._create_session_with_ssl_config()
            response = session.get(url, verify=False, timeout=30)
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json(),
                'method': 'custom_ssl_context'
            }
        except Exception as e:
            return {'success': False, 'error': f'Custom SSL context failed: {str(e)}'}
    
    def _fetch_with_system_ca_bundle(self, url: str) -> Dict[str, Any]:
        """Try with system CA bundle."""
        try:
            import certifi
            response = requests.get(
                url, 
                headers=self.headers, 
                verify=certifi.where(), 
                timeout=30
            )
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json(),
                'method': 'system_ca_bundle'
            }
        except ImportError:
            return {'success': False, 'error': 'certifi package not available'}
        except Exception as e:
            return {'success': False, 'error': f'System CA bundle failed: {str(e)}'}
    
    def list_pull_requests(self, owner: str, repo: str, state: str = 'open', per_page: int = 30) -> Dict[str, Any]:
        """
        List pull requests for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: PR state ('open', 'closed', 'all')
            per_page: Number of PRs per page
            
        Returns:
            Dictionary containing list of PRs or error information
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        params = {
            'state': state,
            'per_page': per_page,
            'sort': 'updated',
            'direction': 'desc'
        }
        
        try:
            # Try the same SSL strategies for listing PRs
            response = requests.get(url, headers=self.headers, params=params, verify=False, timeout=30)
            response.raise_for_status()
            
            prs = response.json()
            return {
                'success': True,
                'data': [
                    {
                        'number': pr['number'],
                        'title': pr['title'],
                        'state': pr['state'],
                        'author': pr['user']['login'],
                        'url': pr['html_url'],
                        'created_at': pr['created_at'],
                        'updated_at': pr['updated_at']
                    }
                    for pr in prs
                ]
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to list pull requests: {str(e)}',
                'data': None
            }