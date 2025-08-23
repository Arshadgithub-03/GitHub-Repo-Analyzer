import os
import requests
from dotenv import load_dotenv
from collections import Counter
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import base64
from io import BytesIO
import re

load_dotenv()

class GitHubRepoAnalyzer:
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        self.headers = {'Authorization': f'token {self.token}'} if self.token else {}
        self.base_url = 'https://api.github.com'
        self.rate_limit_remaining = 60  # Default for unauthenticated requests
        self.request_count = 0
    
    def make_request(self, url):
        """Make API request with rate limit handling"""
        self.request_count += 1
        
        # Add delay for unauthenticated requests to avoid rate limiting
        if not self.headers:
            time.sleep(0.6)
            
        response = requests.get(url, headers=self.headers)
        
        # Update rate limit info
        if 'X-RateLimit-Remaining' in response.headers:
            self.rate_limit_remaining = int(response.headers['X-RateLimit-Remaining'])
        
        # Handle rate limiting
        if response.status_code == 403 and 'rate limit' in response.text.lower():
            reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 60))
            sleep_time = max(reset_time - time.time(), 0) + 10  # Add buffer
            print(f"Rate limit exceeded. Waiting {sleep_time:.0f} seconds...")
            time.sleep(sleep_time)
            # Retry the request after waiting
            return self.make_request(url)
            
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.json().get('message', 'Unknown error')}")
            return None
            
        return response
    
    def get_user_info(self, username):
        """Get user information"""
        url = f"{self.base_url}/users/{username}"
        response = self.make_request(url)
        return response.json() if response else None
    
    def get_user_repos(self, username):
        """Fetch all repositories for a given username"""
        repos = []
        page = 1
        per_page = 100
        
        while True:
            url = f"{self.base_url}/users/{username}/repos?page={page}&per_page={per_page}&sort=updated"
            response = self.make_request(url)
            
            if not response:
                return None
                
            page_repos = response.json()
            if not page_repos:
                break
                
            repos.extend(page_repos)
            
            # Check if we've reached the last page
            if len(page_repos) < per_page:
                break
                
            page += 1
            
        return repos
    
    def get_repo_contributors(self, owner, repo_name):
        """Get contributors for a repository"""
        url = f"{self.base_url}/repos/{owner}/{repo_name}/contributors"
        response = self.make_request(url)
        return response.json() if response else []
    
    def get_repo_commits(self, owner, repo_name):
        """Get recent commits for a repository"""
        # Get commits from the last year
        since_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%SZ')
        url = f"{self.base_url}/repos/{owner}/{repo_name}/commits?since={since_date}&per_page=100"
        response = self.make_request(url)
        return response.json() if response else []
    
    def get_repo_languages(self, owner, repo_name):
        """Get language breakdown for a repository"""
        url = f"{self.base_url}/repos/{owner}/{repo_name}/languages"
        response = self.make_request(url)
        return response.json() if response else {}
    
    def get_repo_readme(self, owner, repo_name):
        """Get README content for a repository"""
        url = f"{self.base_url}/repos/{owner}/{repo_name}/readme"
        response = self.make_request(url)
        if response and response.status_code == 200:
            content = response.json().get('content', '')
            # Decode base64 content
            return base64.b64decode(content).decode('utf-8') if content else None
        return None
    
    def get_repo_activity(self, owner, repo_name):
        """Get repository activity statistics"""
        # Get commit activity (last year)
        url = f"{self.base_url}/repos/{owner}/{repo_name}/stats/commit_activity"
        response = self.make_request(url)
        return response.json() if response else []
    
    def extract_tech_stack(self, readme_text):
        """Extract potential technologies from README"""
        if not readme_text:
            return []
        
        # Common technology keywords to look for
        tech_keywords = [
            'react', 'vue', 'angular', 'django', 'flask', 'express', 'spring',
            'node', 'python', 'javascript', 'typescript', 'java', 'go', 'rust',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'terraform', 'ansible',
            'postgresql', 'mysql', 'mongodb', 'redis', 'graphql', 'webpack', 'babel',
            'jest', 'mocha', 'pytest', 'jenkins', 'github actions', 'travis', 'circleci'
        ]
        
        found_tech = []
        readme_lower = readme_text.lower()
        
        for tech in tech_keywords:
            if tech in readme_lower:
                found_tech.append(tech)
                
        return found_tech
    
    def analyze_repos(self, repos, username):
        """Analyze repository data with enhanced metrics"""
        if not repos:
            return None
            
        # Extract relevant information
        repo_data = []
        language_counter = Counter()
        total_stars = 0
        total_forks = 0
        total_size = 0
        total_watchers = 0
        total_issues = 0
        license_counter = Counter()
        today = datetime.now()
        tech_stack_counter = Counter()
        
        # Get additional data for each repo
        for repo in repos:
            name = repo['name']
            owner = repo['owner']['login']
            language = repo['language'] or 'Unknown'
            stars = repo['stargazers_count']
            forks = repo['forks_count']
            size = repo['size']
            url = repo['html_url']
            description = repo['description'] or 'No description'
            created_at = repo['created_at']
            updated_at = repo['updated_at']
            watchers = repo['watchers_count']
            open_issues = repo['open_issues_count']
            license_info = repo['license']['key'] if repo['license'] else 'None'
            is_fork = repo['fork']
            default_branch = repo['default_branch']
            has_wiki = repo['has_wiki']
            has_pages = repo['has_pages']
            archived = repo['archived']
            
            # Calculate repo age
            created_date = datetime.strptime(created_at[:10], "%Y-%m-%d")
            repo_age_days = (today - created_date).days
            
            # Calculate days since last update
            updated_date = datetime.strptime(updated_at[:10], "%Y-%m-%d")
            days_since_update = (today - updated_date).days
            
            # Get additional details
            languages = self.get_repo_languages(owner, name)
            contributors = self.get_repo_contributors(owner, name)
            commits = self.get_repo_commits(owner, name)
            readme = self.get_repo_readme(owner, name)
            
            # Extract tech stack from README
            tech_stack = self.extract_tech_stack(readme)
            tech_stack_counter.update(tech_stack)
            
            repo_data.append({
                'name': name,
                'owner': owner,
                'language': language,
                'languages': languages,
                'stars': stars,
                'forks': forks,
                'size': size,
                'url': url,
                'description': description,
                'created_at': created_at,
                'updated_at': updated_at,
                'watchers': watchers,
                'open_issues': open_issues,
                'license': license_info,
                'is_fork': is_fork,
                'default_branch': default_branch,
                'has_wiki': has_wiki,
                'has_pages': has_pages,
                'archived': archived,
                'repo_age_days': repo_age_days,
                'days_since_update': days_since_update,
                'contributors_count': len(contributors),
                'commits_count': len(commits),
                'tech_stack': tech_stack,
                'readme': readme
            })
            
            if language:  # Only count if language is not None
                language_counter.update([language])
                
            total_stars += stars
            total_forks += forks
            total_size += size
            total_watchers += watchers
            total_issues += open_issues
            license_counter.update([license_info])
        
        # Calculate additional metrics
        active_repos = sum(1 for repo in repo_data if repo['days_since_update'] < 90)  # Updated in last 90 days
        archived_repos = sum(1 for repo in repo_data if repo['archived'])
        fork_repos = sum(1 for repo in repo_data if repo['is_fork'])
        
        # Find most used language
        most_used_language = language_counter.most_common(1)
        most_used_language = most_used_language[0] if most_used_language else ('None', 0)
        
        # Calculate average repo age
        avg_repo_age = sum(repo['repo_age_days'] for repo in repo_data) / len(repo_data) if repo_data else 0
        
        # Calculate average time since last update
        avg_days_since_update = sum(repo['days_since_update'] for repo in repo_data) / len(repo_data) if repo_data else 0
        
        # Calculate average contributors
        avg_contributors = sum(repo['contributors_count'] for repo in repo_data) / len(repo_data) if repo_data else 0
        
        # Calculate average commits
        avg_commits = sum(repo['commits_count'] for repo in repo_data) / len(repo_data) if repo_data else 0
        
        return {
            'repo_count': len(repos),
            'repos': repo_data,
            'most_used_language': most_used_language[0],
            'language_count': most_used_language[1],
            'total_stars': total_stars,
            'total_forks': total_forks,
            'total_size': total_size,
            'total_watchers': total_watchers,
            'total_issues': total_issues,
            'language_distribution': dict(language_counter),
            'license_distribution': dict(license_counter),
            'tech_stack_distribution': dict(tech_stack_counter),
            'avg_stars': total_stars / len(repos) if repos else 0,
            'avg_forks': total_forks / len(repos) if repos else 0,
            'avg_watchers': total_watchers / len(repos) if repos else 0,
            'avg_issues': total_issues / len(repos) if repos else 0,
            'active_repos': active_repos,
            'archived_repos': archived_repos,
            'fork_repos': fork_repos,
            'avg_repo_age': avg_repo_age,
            'avg_days_since_update': avg_days_since_update,
            'avg_contributors': avg_contributors,
            'avg_commits': avg_commits,
            'request_count': self.request_count,
            'rate_limit_remaining': self.rate_limit_remaining
        }
    
    def get_user_activity(self, username):
        """Get user activity events"""
        url = f"{self.base_url}/users/{username}/events"
        response = self.make_request(url)
        return response.json() if response else []
    
    def analyze_user_activity(self, events):
        """Analyze user activity from events"""
        if not events:
            return {}
            
        event_types = Counter()
        repo_activity = Counter()
        
        for event in events:
            event_type = event['type']
            event_types[event_type] += 1
            
            if 'repo' in event:
                repo_name = event['repo']['name']
                repo_activity[repo_name] += 1
        
        return {
            'event_types': dict(event_types),
            'repo_activity': dict(repo_activity)
        }