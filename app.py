import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from github_analyzer import GitHubRepoAnalyzer

# Page configuration
st.set_page_config(
    page_title="GitHub Repo Analyzer",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {font-size: 3rem; color: #6e5494;}
    .metric-card {background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 10px;}
    .metric-value {font-size: 2rem; font-weight: bold;}
    .metric-label {font-size: 1rem; color: #666;}
    .repo-card {background-color: #f9f9f9; padding: 15px; border-radius: 10px; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<h1 class="main-header">GitHub Repository Analyzer</h1>', unsafe_allow_html=True)
st.write("Analyze any GitHub user's repositories, programming languages, and project metrics.")

# Sidebar for input
with st.sidebar:
    st.header("Configuration")
    username = st.text_input("GitHub Username", value="torvalds")
    analyze_button = st.button("Analyze Repositories")
    
    st.markdown("---")
    st.info("""
    This tool fetches public repository data from GitHub using their API.
    Note: Private repositories won't be included unless you authenticate.
    """)

# Initialize analyzer
analyzer = GitHubRepoAnalyzer()

if analyze_button and username:
    with st.spinner(f"Fetching repositories for {username}..."):
        repos = analyzer.get_user_repos(username)
        
    if repos is None:
        st.error("User not found or API rate limit exceeded. Try again later.")
    elif not repos:
        st.warning("This user has no repositories or they are all private.")
    else:
        analysis = analyzer.analyze_repos(repos)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{analysis["repo_count"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Repositories</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{analysis["most_used_language"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Most Used Language</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{analysis["total_stars"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Stars</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{analysis["total_forks"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Forks</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Additional metrics
        col5, col6, col7 = st.columns(3)
        
        with col5:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{analysis["total_size"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Size (KB)</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col6:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{analysis["avg_stars"]:.1f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Avg Stars/Repo</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col7:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{analysis["avg_forks"]:.1f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Avg Forks/Repo</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Language distribution chart
        st.subheader("Language Distribution")
        lang_data = [{"Language": k, "Count": v} for k, v in analysis["language_distribution"].items() if k and k != "Unknown"]
        if lang_data:
            fig = px.pie(lang_data, values='Count', names='Language', 
                         title='Programming Languages Used')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No language data available.")
        
        # Repositories table
        st.subheader("Repository Details")
        sorted_repos = sorted(analysis["repos"], key=lambda x: x["stars"], reverse=True)
        
        # Create a DataFrame-like display
        for i, repo in enumerate(sorted_repos):
            with st.expander(f"{i+1}. {repo['name']} | ⭐ {repo['stars']} | 🍴 {repo['forks']} | {repo['language'] or 'Unknown'}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Language:** {repo['language']}")
                    st.write(f"**Stars:** {repo['stars']}")
                    st.write(f"**Forks:** {repo['forks']}")
                with col2:
                    st.write(f"**Size:** {repo['size']} KB")
                    st.write(f"**Created:** {repo['created_at'][:10]}")
                    st.write(f"**Updated:** {repo['updated_at'][:10]}")
                
                st.write(f"**Description:** {repo['description']}")
                st.markdown(f"[View on GitHub]({repo['url']})")
                
else:
    st.info("👈 Enter a GitHub username in the sidebar and click 'Analyze Repositories' to get started.")
    st.image("https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png", width=200)

# Footer
st.markdown("---")
st.markdown("Built with Python, Streamlit, and the GitHub API")