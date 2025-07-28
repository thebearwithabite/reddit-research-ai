import runpod
import requests
import json
import os
from datetime import datetime
import re
from typing import Dict, List, Any

# Configuration
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
SUBSTACK_ENDPOINTS = [
    'https://magazine.sebastianraschka.com',
    'https://www.understandingai.org',
    'https://garymarcus.substack.com',
    'https://oneusefulthing.substack.com',  # Ethan Mollick
    'https://www.ai-supremacy.com',  # Michael Spencer
    'https://aiscientist.substack.com',
    'https://newsletter.towardsai.net'
]

def extract_substack_posts(newsletter_url: str, limit: int = 5) -> List[Dict]:
    """Extract recent posts from a Substack newsletter"""
    try:
        # Try to get RSS feed first (most reliable)
        rss_url = f"{newsletter_url}/feed"
        response = requests.get(rss_url, timeout=10)
        
        if response.status_code == 200:
            # Parse RSS (simplified - in production we'd use feedparser)
            content = response.text
            
            # Extract post data using regex (basic implementation)
            posts = []
            # This is a simplified parser - in production we'd use proper RSS parsing
            title_pattern = r'<title><!\[CDATA\[(.*?)\]\]></title>'
            link_pattern = r'<link>(.*?)</link>'
            description_pattern = r'<description><!\[CDATA\[(.*?)\]\]></description>'
            
            titles = re.findall(title_pattern, content)
            links = re.findall(link_pattern, content)
            descriptions = re.findall(description_pattern, content)
            
            for i in range(min(limit, len(titles))):
                if i < len(titles) and i < len(links):
                    posts.append({
                        'title': titles[i],
                        'url': links[i],
                        'excerpt': descriptions[i] if i < len(descriptions) else '',
                        'source': newsletter_url,
                        'scraped_at': datetime.now().isoformat()
                    })
            
            return posts
        else:
            return []
            
    except Exception as e:
        print(f"Error scraping {newsletter_url}: {str(e)}")
        return []

def analyze_posts_with_claude(posts: List[Dict]) -> Dict:
    """Analyze posts using Claude API for research intelligence"""
    
    if not ANTHROPIC_API_KEY:
        return {"error": "No Anthropic API key configured"}
    
    # Prepare content for analysis
    content_summary = ""
    for post in posts:
        content_summary += f"Title: {post['title']}\n"
        content_summary += f"Source: {post['source']}\n"
        content_summary += f"Excerpt: {post['excerpt'][:500]}...\n\n"
    
    analysis_prompt = f"""
    Analyze these AI consciousness/research newsletter posts for storytelling and collaboration opportunities:

    {content_summary}

    Please provide:
    1. Key themes across these posts
    2. Potential story angles for a podcast about AI consciousness
    3. Researchers who might be open to creative collaboration
    4. Emotional undertones or personal elements in the writing
    5. Connections between different authors' work
    6. Specific collaboration opportunities

    Focus on finding the human stories behind the technical content.
    """
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': ANTHROPIC_API_KEY,
            'anthropic-version': '2023-06-01'
        }
        
        payload = {
            'model': 'claude-3-sonnet-20240229',
            'max_tokens': 2000,
            'messages': [
                {
                    'role': 'user',
                    'content': analysis_prompt
                }
            ]
        }
        
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                'analysis': result['content'][0]['text'],
                'timestamp': datetime.now().isoformat(),
                'posts_analyzed': len(posts)
            }
        else:
            return {"error": f"Claude API error: {response.status_code}"}
            
    except Exception as e:
        return {"error": f"Analysis error: {str(e)}"}

def collect_research_intelligence(event: Dict) -> Dict:
    """Main function to collect and analyze newsletter data"""
    
    # Get parameters from the event
    newsletters = event.get('newsletters', SUBSTACK_ENDPOINTS)
    posts_per_newsletter = event.get('posts_per_newsletter', 3)
    
    all_posts = []
    
    # Collect posts from each newsletter
    for newsletter_url in newsletters:
        print(f"Scraping: {newsletter_url}")
        posts = extract_substack_posts(newsletter_url, posts_per_newsletter)
        all_posts.extend(posts)
    
    # Analyze with Claude
    print(f"Analyzing {len(all_posts)} posts with Claude...")
    analysis = analyze_posts_with_claude(all_posts)
    
    return {
        'statusCode': 200,
        'body': {
            'posts_collected': len(all_posts),
            'posts': all_posts,
            'ai_analysis': analysis,
            'generated_at': datetime.now().isoformat()
        }
    }

def handler(event):
    """RunPod serverless handler"""
    try:
        result = collect_research_intelligence(event['input'])
        return result
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {
                'error': str(e)
            }
        }

# Initialize RunPod serverless
runpod.serverless.start({"handler": handler})