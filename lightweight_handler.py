import runpod
import requests
import json
import os
from datetime import datetime

# Simple test version - minimal dependencies
def handler(event):
    """Lightweight test handler"""
    
    job_input = event.get('input', {})
    
    # Check if this is just a test
    if 'test' in job_input:
        return {
            'message': 'Handler working!',
            'test_input': job_input.get('test'),
            'timestamp': datetime.now().isoformat(),
            'environment_check': {
                'anthropic_key_set': bool(os.environ.get('ANTHROPIC_API_KEY')),
                'python_version': '3.x working'
            }
        }
    
    # Basic newsletter test
    newsletters = job_input.get('newsletters', ['https://garymarcus.substack.com'])
    
    try:
        # Simple RSS fetch test
        test_url = newsletters[0] + '/feed'
        response = requests.get(test_url, timeout=10)
        
        result = {
            'test_mode': True,
            'rss_fetch_status': response.status_code,
            'rss_content_length': len(response.text) if response.status_code == 200 else 0,
            'timestamp': datetime.now().isoformat(),
            'next_step': 'RSS fetch working, ready for full implementation'
        }
        
        # If Anthropic key is set, test that too
        anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        if anthropic_key:
            result['anthropic_key_configured'] = True
            result['anthropic_key_prefix'] = anthropic_key[:10] + '...'
        else:
            result['anthropic_key_configured'] = False
            
        return result
        
    except Exception as e:
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'debug': 'Basic functionality test failed'
        }

# Start the serverless worker
if __name__ == '__main__':
    runpod.serverless.start({'handler': handler})