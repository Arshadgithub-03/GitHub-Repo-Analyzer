import os
import requests
from dotenv import load_dotenv
from collections import Counter
import time

load_dotenv()

class GitHubRepoAnalyzer:
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        self.headers = {'Authorization': f'token {self.token}'} if self.token else {}
        self.base_url = 'https://api.github.com'
    
    def get_user_repos(self, username):
        """Fetch all repositories for a given username"""
        repos = []
        page = 1
        per_page = 100
        
        while True:
            url = f"{self.base_url}/users/{username}/repos?page={page}&per_page={per_page}"
            response = requests.get(url, headers=self.headers)
            
            # Handle rate limiting
            if response.status_code == 403 and 'rate limit' in response.text.lower():
                reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 60))
                sleep_time = max(reset_time - time.time(), 0) + 10  # Add buffer
                print(f"Rate limit exceeded. Waiting {sleep_time:.0f} seconds...")
                time.sleep(sleep_time)
                continue
                
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.json().get('message', 'Unknown error')}")
                return None
                
            page_repos = response.json()
            if not page_repos:
                break
                
            repos.extend(page_repos)
            page += 1
            
            # Add a small delay to be respectful of API limits
            time.sleep(0.1)
            
        return repos
    
    def analyze_repos(self, repos):
        """Analyze repository data"""
        if not repos:
            return None
            
        # Extract relevant information
        repo_data = []
        language_counter = Counter()
        total_stars = 0
        total_forks = 0
        total_size = 0
        
        for repo in repos:
            name = repo['name']
            language = repo['language'] or 'Unknown'
            stars = repo['stargazers_count']
            forks = repo['forks_count']
            size = repo['size']
            url = repo['html_url']
            description = repo['description'] or 'No description'
            created_at = repo['created_at']
            updated_at = repo['updated_at']
            
            repo_data.append({
                'name': name,
                'language': language,
                'stars': stars,
                'forks': forks,
                'size': size,
                'url': url,
                'description': description,
                'created_at': created_at,
                'updated_at': updated_at
            })
            
            if language:  # Only count if language is not None
                language_counter.update([language])
            total_stars += stars
            total_forks += forks
            total_size += size
        
        # Find most used language
        most_used_language = language_counter.most_common(1)
        most_used_language = most_used_language[0] if most_used_language else ('None', 0)
        
        return {
            'repo_count': len(repos),
            'repos': repo_data,
            'most_used_language': most_used_language[0],
            'language_count': most_used_language[1],
            'total_stars': total_stars,
            'total_forks': total_forks,
            'total_size': total_size,
            'language_distribution': dict(language_counter),
            'avg_stars': total_stars / len(repos) if repos else 0,
            'avg_forks': total_forks / len(repos) if repos else 0
        }
    
    def display_results(self, username, analysis):
        """Display results in CLI"""
        print(f"\n{'='*50}")
        print(f"GitHub Repository Analysis for {username}")
        print(f"{'='*50}")
        print(f"Total repositories: {analysis['repo_count']}")
        print(f"Most used language: {analysis['most_used_language']} ({analysis['language_count']} repos)")
        print(f"Total stars: {analysis['total_stars']}")
        print(f"Total forks: {analysis['total_forks']}")
        print(f"Total size: {analysis['total_size']} KB")
        print(f"Average stars per repo: {analysis['avg_stars']:.2f}")
        print(f"Average forks per repo: {analysis['avg_forks']:.2f}")
        
        print("\nLanguage distribution:")
        for lang, count in analysis['language_distribution'].items():
            if lang != 'Unknown':  # Skip unknown languages
                print(f"  {lang}: {count}")
        
        print("\nTop 5 repositories by stars:")
        sorted_repos = sorted(analysis['repos'], key=lambda x: x['stars'], reverse=True)
        for i, repo in enumerate(sorted_repos[:5]):
            print(f"  {i+1}. {repo['name']} - {repo['stars']} stars, {repo['forks']} forks")
            print(f"     Language: {repo['language']}, Size: {repo['size']} KB")
            print(f"     Description: {repo['description']}")
            print()

def main():
    analyzer = GitHubRepoAnalyzer()
    username = input("Enter GitHub username: ").strip()
    
    if not username:
        print("Username cannot be empty!")
        return
    
    print(f"Fetching repositories for {username}...")
    repos = analyzer.get_user_repos(username)
    
    if repos is not None:
        analysis = analyzer.analyze_repos(repos)
        if analysis:
            analyzer.display_results(username, analysis)
        else:
            print("No repositories found or error in analysis.")
    else:
        print("Failed to fetch repositories.")

if __name__ == "__main__":
    main()