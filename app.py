import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
from github_analyzer import GitHubRepoAnalyzer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Page configuration
st.set_page_config(
    page_title="GitHub Repo Analyzer Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {font-size: 3rem; color: #6e5494; margin-bottom: 0.5rem;}
    .sub-header {font-size: 1.5rem; color: #4078c0; margin-top: 1.5rem;}
    .metric-card {background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);}
    .metric-value {font-size: 2rem; font-weight: bold; color: #6e5494;}
    .metric-label {font-size: 1rem; color: #666;}
    .repo-card {background-color: #f9f9f9; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #6e5494;}
    .info-box {background-color: #e6f7ff; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid #1890ff;}
    .warning-box {background-color: #fff7e6; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid #fa8c16;}
    .success-box {background-color: #f6ffed; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid #52c41a;}
    .tab-content {padding: 20px 0;}
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<h1 class="main-header">GitHub Repository Analyzer Pro</h1>', unsafe_allow_html=True)
st.write("Comprehensive analysis of GitHub users' repositories, programming languages, and development activity.")

# Sidebar for input
with st.sidebar:
    st.header("Configuration")
    username = st.text_input("GitHub Username", value="torvalds")
    
    # Analysis options
    st.subheader("Analysis Options")
    include_user_info = st.checkbox("Include User Profile", value=True)
    include_activity = st.checkbox("Include Activity Analysis", value=True)
    include_tech_stack = st.checkbox("Include Tech Stack Analysis", value=True)
    
    analyze_button = st.button("Analyze Repositories", type="primary")
    
    st.markdown("---")
    st.info("""
    **Tips:**
    - Add a GITHUB_TOKEN in .env for higher rate limits
    - For organizations, use the organization name
    - Private repos are only visible with proper authentication
    """)
    
    # Rate limit info placeholder
    rate_limit_placeholder = st.empty()

# Initialize analyzer
analyzer = GitHubRepoAnalyzer()

if analyze_button and username:
    with st.spinner(f"Fetching data for {username}..."):
        # Get user info
        user_info = analyzer.get_user_info(username) if include_user_info else None
        
        # Get repositories
        repos = analyzer.get_user_repos(username)
        
        # Get user activity
        events = analyzer.get_user_activity(username) if include_activity else None
        activity_analysis = analyzer.analyze_user_activity(events) if events else None
        
    if repos is None:
        st.error("User not found or API rate limit exceeded. Try again later.")
    elif not repos:
        st.warning("This user has no repositories or they are all private.")
    else:
        analysis = analyzer.analyze_repos(repos, username)
        
        # Update rate limit info in sidebar
        rate_limit_placeholder.info(f"API Requests: {analysis['request_count']} | Remaining: {analysis['rate_limit_remaining']}")
        
        # Display user info if available
        if user_info:
            with st.expander("User Profile", expanded=True):
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    st.image(user_info.get('avatar_url', ''), width=150)
                
                with col2:
                    st.subheader(user_info.get('name', username))
                    st.write(user_info.get('bio', 'No bio available'))
                    st.write(f"📍 {user_info.get('location', 'Not specified')}")
                    st.write(f"👥 Followers: {user_info.get('followers', 0)} | Following: {user_info.get('following', 0)}")
                    
                with col3:
                    st.write(f"📊 Public repos: {user_info.get('public_repos', 0)}")
                    st.write(f"📝 Public gists: {user_info.get('public_gists', 0)}")
                    st.write(f"🕒 Created: {user_info.get('created_at', '')[:10]}")
        
        # Display metrics in tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Languages", "Repositories", "Activity", "Tech Stack"])
        
        with tab1:
            st.markdown('<div class="sub-header">Overview Metrics</div>', unsafe_allow_html=True)
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{analysis["repo_count"]}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Total Repositories</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{analysis["most_used_language"]}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Top Language</div>', unsafe_allow_html=True)
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
            col5, col6, col7, col8 = st.columns(4)
            
            with col5:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{analysis["active_repos"]}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Active Repos (90d)</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col6:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{analysis["fork_repos"]}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Forked Repos</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col7:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{analysis["archived_repos"]}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Archived Repos</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col8:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{analysis["avg_contributors"]:.1f}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Avg Contributors</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Repository age and activity
            col9, col10, col11, col12 = st.columns(4)
            
            with col9:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{analysis["avg_repo_age"]:.0f}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Avg Repo Age (days)</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col10:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{analysis["avg_days_since_update"]:.0f}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Avg Days Since Update</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col11:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{analysis["avg_commits"]:.0f}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Avg Commits (last year)</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col12:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{analysis["total_issues"]}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Open Issues</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Activity summary
            st.markdown('<div class="sub-header">Repository Health Summary</div>', unsafe_allow_html=True)
            
            # Calculate health score based on various factors
            health_score = 0
            max_score = 100
            
            # Score based on activity (days since update)
            if analysis["avg_days_since_update"] < 30:
                health_score += 30
                activity_status = "Very Active"
            elif analysis["avg_days_since_update"] < 90:
                health_score += 20
                activity_status = "Active"
            elif analysis["avg_days_since_update"] < 180:
                health_score += 10
                activity_status = "Moderately Active"
            else:
                activity_status = "Inactive"
            
            # Score based on community engagement
            engagement = (analysis["avg_stars"] + analysis["avg_forks"]) / 2
            if engagement > 50:
                health_score += 30
                engagement_status = "High Engagement"
            elif engagement > 10:
                health_score += 20
                engagement_status = "Good Engagement"
            elif engagement > 1:
                health_score += 10
                engagement_status = "Low Engagement"
            else:
                engagement_status = "Minimal Engagement"
            
            # Score based on maintenance (issues and archived status)
            issue_ratio = analysis["total_issues"] / analysis["repo_count"] if analysis["repo_count"] > 0 else 0
            if issue_ratio < 5 and analysis["archived_repos"] == 0:
                health_score += 40
                maintenance_status = "Well Maintained"
            elif issue_ratio < 10 and analysis["archived_repos"] / analysis["repo_count"] < 0.2:
                health_score += 25
                maintenance_status = "Moderately Maintained"
            else:
                maintenance_status = "Needs Attention"
            
            # Display health score
            health_col1, health_col2, health_col3 = st.columns(3)
            
            with health_col1:
                st.plotly_chart(go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = health_score,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Health Score"},
                    gauge = {
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 33], 'color': "lightcoral"},
                            {'range': [33, 66], 'color': "lightyellow"},
                            {'range': [66, 100], 'color': "lightgreen"}
                        ]
                    }
                )), use_container_width=True)
            
            with health_col2:
                st.markdown("**Activity Status:**")
                st.info(f"📈 {activity_status}")
                
                st.markdown("**Engagement Status:**")
                st.info(f"👥 {engagement_status}")
                
            with health_col3:
                st.markdown("**Maintenance Status:**")
                st.info(f"🔧 {maintenance_status}")
        
        with tab2:
            st.markdown('<div class="sub-header">Language Analysis</div>', unsafe_allow_html=True)
            
            # Language distribution chart
            lang_data = [{"Language": k, "Count": v} for k, v in analysis["language_distribution"].items() if k and k != "Unknown"]
            
            if lang_data:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.pie(lang_data, values='Count', names='Language', 
                                title='Programming Languages Distribution')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Prepare data for bar chart
                    lang_df = pd.DataFrame(lang_data).sort_values('Count', ascending=False)
                    fig = px.bar(lang_df, x='Language', y='Count', 
                                title='Languages by Repository Count')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Detailed language breakdown by bytes
                st.markdown("**Detailed Language Breakdown**")
                
                # Collect language bytes data from all repos
                language_bytes = {}
                for repo in analysis['repos']:
                    if repo['languages']:
                        for lang, bytes_count in repo['languages'].items():
                            if lang in language_bytes:
                                language_bytes[lang] += bytes_count
                            else:
                                language_bytes[lang] = bytes_count
                
                if language_bytes:
                    # Convert to MB for readability
                    language_mb = {k: v / 1024 for k, v in language_bytes.items()}
                    lang_bytes_data = [{"Language": k, "Size (MB)": v} for k, v in language_mb.items()]
                    lang_bytes_df = pd.DataFrame(lang_bytes_data).sort_values('Size (MB)', ascending=False)
                    
                    fig = px.bar(lang_bytes_df.head(10), x='Language', y='Size (MB)', 
                                title='Top Languages by Code Size (MB)')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No detailed language data available.")
            else:
                st.info("No language data available.")
        
        with tab3:
            st.markdown('<div class="sub-header">Repository Details</div>', unsafe_allow_html=True)
            
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filter_language = st.selectbox("Filter by Language", 
                                             options=["All"] + list(analysis["language_distribution"].keys()))
            
            with col2:
                sort_option = st.selectbox("Sort by", 
                                         options=["Stars", "Forks", "Recent Update", "Size", "Age"])
            
            with col3:
                min_stars = st.slider("Minimum Stars", 0, 1000, 0)
            
            # Apply filters
            filtered_repos = analysis["repos"]
            
            if filter_language != "All":
                filtered_repos = [repo for repo in filtered_repos if repo["language"] == filter_language]
            
            filtered_repos = [repo for repo in filtered_repos if repo["stars"] >= min_stars]
            
            # Apply sorting
            if sort_option == "Stars":
                filtered_repos.sort(key=lambda x: x["stars"], reverse=True)
            elif sort_option == "Forks":
                filtered_repos.sort(key=lambda x: x["forks"], reverse=True)
            elif sort_option == "Size":
                filtered_repos.sort(key=lambda x: x["size"], reverse=True)
            elif sort_option == "Age":
                filtered_repos.sort(key=lambda x: x["repo_age_days"], reverse=True)
            else:  # Recent Update
                filtered_repos.sort(key=lambda x: x["updated_at"], reverse=True)
            
            # Display repositories
            for i, repo in enumerate(filtered_repos):
                with st.expander(f"{i+1}. {repo['name']} | ⭐ {repo['stars']} | 🍴 {repo['forks']} | {repo['language'] or 'Unknown'}", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Language:** {repo['language']}")
                        st.write(f"**Stars:** {repo['stars']}")
                        st.write(f"**Forks:** {repo['forks']}")
                        st.write(f"**Watchers:** {repo['watchers']}")
                    
                    with col2:
                        st.write(f"**Size:** {repo['size']} KB")
                        st.write(f"**Open Issues:** {repo['open_issues']}")
                        st.write(f"**License:** {repo['license']}")
                        st.write(f"**Contributors:** {repo['contributors_count']}")
                    
                    with col3:
                        st.write(f"**Created:** {repo['created_at'][:10]}")
                        st.write(f"**Updated:** {repo['updated_at'][:10]}")
                        st.write(f"**Age:** {repo['repo_age_days']} days")
                        st.write(f"**Last Update:** {repo['days_since_update']} days ago")
                    
                    st.write(f"**Description:** {repo['description']}")
                    
                    # Show README preview if available
                    if repo['readme']:
                        with st.expander("README Preview"):
                            # Display first 500 characters of README
                            readme_preview = repo['readme'][:500] + "..." if len(repo['readme']) > 500 else repo['readme']
                            st.text(readme_preview)
                    st.markdown(f"[View on GitHub]({repo['url']})")
        
        with tab4:
            st.markdown('<div class="sub-header">Activity Analysis</div>', unsafe_allow_html=True)
            
            if activity_analysis:
                # Event types chart
                event_data = [{"Event Type": k, "Count": v} for k, v in activity_analysis["event_types"].items()]
                if event_data:
                    event_df = pd.DataFrame(event_data).sort_values('Count', ascending=False)
                    fig = px.bar(event_df, x='Event Type', y='Count', 
                                title='User Activity by Event Type')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Repository activity chart
                repo_activity_data = [{"Repository": k, "Activity": v} for k, v in activity_analysis["repo_activity"].items()]
                if repo_activity_data:
                    repo_activity_df = pd.DataFrame(repo_activity_data).sort_values('Activity', ascending=False).head(10)
                    fig = px.bar(repo_activity_df, x='Repository', y='Activity', 
                                title='Most Active Repositories')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No activity data available. This might be due to rate limiting or user privacy settings.")
            
            # Repository update timeline
            st.markdown("**Repository Update Timeline**")
            
            # Prepare data for update timeline
            update_data = []
            for repo in analysis['repos']:
                if repo['updated_at']:
                    update_data.append({
                        'Repository': repo['name'],
                        'Last Update': repo['updated_at'][:10],
                        'Days Since Update': repo['days_since_update'],
                        'Stars': repo['stars']
                    })
            
            if update_data:
                update_df = pd.DataFrame(update_data)
                update_df['Last Update'] = pd.to_datetime(update_df['Last Update'])
                update_df = update_df.sort_values('Last Update')
                
                fig = px.scatter(update_df, x='Last Update', y='Repository', 
                                size='Stars', color='Days Since Update',
                                title='Repository Update Timeline',
                                labels={'Last Update': 'Date of Last Update', 'Repository': 'Repository Name'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No update data available.")
        
        with tab5:
            st.markdown('<div class="sub-header">Technology Stack Analysis</div>', unsafe_allow_html=True)
            
            if analysis["tech_stack_distribution"]:
                # Tech stack chart
                tech_data = [{"Technology": k, "Count": v} for k, v in analysis["tech_stack_distribution"].items()]
                tech_df = pd.DataFrame(tech_data).sort_values('Count', ascending=False)
                
                fig = px.bar(tech_df, x='Technology', y='Count', 
                            title='Technology Stack Distribution')
                st.plotly_chart(fig, use_container_width=True)
                
                # Tech stack word cloud
                st.markdown("**Technology Word Cloud**")
                
                # Generate word cloud
                wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(analysis["tech_stack_distribution"])
                
                # Display the word cloud
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
                
                # Tech stack by repository
                st.markdown("**Technologies by Repository**")
                
                tech_repo_data = []
                for repo in analysis['repos']:
                    for tech in repo['tech_stack']:
                        tech_repo_data.append({
                            'Repository': repo['name'],
                            'Technology': tech,
                            'Stars': repo['stars']
                        })
                
                if tech_repo_data:
                    tech_repo_df = pd.DataFrame(tech_repo_data)
                    
                    # Pivot table for heatmap
                    heatmap_data = tech_repo_df.groupby(['Repository', 'Technology']).size().unstack(fill_value=0)
                    
                    # Create heatmap
                    fig = px.imshow(heatmap_data.T, 
                                    title='Technologies Used in Each Repository',
                                    aspect='auto')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No technology-repository mapping data available.")
            else:
                st.info("No technology stack data found in README files.")
        
        # Export options
        st.markdown("---")
        st.markdown('<div class="sub-header">Export Data</div>', unsafe_allow_html=True)
        
        # Create DataFrame for export
        export_data = []
        for repo in analysis['repos']:
            export_data.append({
                'Name': repo['name'],
                'Language': repo['language'],
                'Stars': repo['stars'],
                'Forks': repo['forks'],
                'Size_KB': repo['size'],
                'Watchers': repo['watchers'],
                'Open_Issues': repo['open_issues'],
                'Created_At': repo['created_at'],
                'Updated_At': repo['updated_at'],
                'Days_Since_Update': repo['days_since_update'],
                'Repo_Age_Days': repo['repo_age_days'],
                'Contributors': repo['contributors_count'],
                'Commits_Last_Year': repo['commits_count'],
                'License': repo['license'],
                'Is_Fork': repo['is_fork'],
                'Archived': repo['archived']
            })
        
        export_df = pd.DataFrame(export_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV export
            csv = export_df.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name=f"github_repos_{username}.csv",
                mime="text/csv"
            )
        
        with col2:
            # JSON export
            json = export_df.to_json(indent=2, orient='records')
            st.download_button(
                label="Download as JSON",
                data=json,
                file_name=f"github_repos_{username}.json",
                mime="application/json"
            )
                
else:
    st.info("👈 Enter a GitHub username in the sidebar and click 'Analyze Repositories' to get started.")
    
    # Display sample analysis for demonstration
    with st.expander("See sample analysis"):
        st.write("""
        This tool provides comprehensive analysis of GitHub users' repositories including:
        
        - **Overview Metrics**: Total repos, stars, forks, and more
        - **Language Analysis**: Programming language distribution and trends
        - **Repository Details**: Detailed information about each repository
        - **Activity Analysis**: User activity and repository update patterns
        - **Tech Stack Analysis**: Technologies mentioned in README files
        
        To get started, enter a GitHub username in the sidebar and click the analyze button.
        """)
        
        st.image("https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png", width=200)

# Footer
st.markdown("---")
st.markdown("Built with Python, Streamlit, and the GitHub API | [GitHub](https://github.com)")