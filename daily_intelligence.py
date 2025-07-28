import requests
import json
import time
from datetime import datetime

# Configuration
RUNPOD_API_KEY = "YOUR_RUNPOD_API_KEY"  # Replace with your actual key
ENDPOINT_URL = "YOUR_ENDPOINT_URL"      # Replace with your actual endpoint URL

# All the AI consciousness researchers we're tracking
ALL_NEWSLETTERS = [
    "https://garymarcus.substack.com",
    "https://magazine.sebastianraschka.com", 
    "https://oneusefulthing.substack.com",
    "https://www.understandingai.org",
    "https://www.ai-supremacy.com",
    "https://aiscientist.substack.com",
    "https://newsletter.towardsai.net",
    "https://exponentialview.substack.com",
    "https://www.interconnects.ai",
    "https://cameronrwolfe.substack.com"
]

def run_research_intelligence(newsletters=None, posts_per_newsletter=3):
    """Run the research intelligence collection"""
    
    if newsletters is None:
        newsletters = ALL_NEWSLETTERS
    
    payload = {
        "input": {
            "newsletters": newsletters,
            "posts_per_newsletter": posts_per_newsletter,
            "include_outreach_strategy": True
        }
    }
    
    headers = {
        "Authorization": f"{RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"🚀 Starting research intelligence run...")
    print(f"📊 Scanning {len(newsletters)} newsletters")
    
    # Start the job
    response = requests.post(ENDPOINT_URL, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"❌ Error starting job: {response.status_code}")
        print(response.text)
        return None
    
    job_data = response.json()
    job_id = job_data['id']
    
    print(f"⏳ Job started: {job_id}")
    print("Processing... this may take 2-3 minutes")
    
    # Poll for results
    status_url = f"{ENDPOINT_URL.replace('/run', '')}/stream/{job_id}"
    
    while True:
        status_response = requests.get(status_url, headers=headers)
        if status_response.status_code == 200:
            status_data = status_response.json()
            
            if status_data['status'] == 'COMPLETED':
                print("✅ Analysis complete!")
                return status_data['output']
            elif status_data['status'] == 'FAILED':
                print("❌ Job failed")
                print(status_data.get('error', 'Unknown error'))
                return None
            else:
                print(f"⏳ Status: {status_data['status']}")
                time.sleep(10)
        else:
            print(f"❌ Error checking status: {status_response.status_code}")
            return None

def save_intelligence_report(data, filename=None):
    """Save the intelligence report to a file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_intelligence_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 Report saved to: {filename}")
    return filename

def print_summary(data):
    """Print a quick summary of the findings"""
    if not data or 'research_intelligence' not in data:
        print("❌ No intelligence data to summarize")
        return
    
    print("\n" + "="*60)
    print("🧠 RESEARCH INTELLIGENCE SUMMARY")
    print("="*60)
    print(f"📊 Posts analyzed: {data.get('posts_collected', 0)}")
    print(f"📰 Newsletters scanned: {data.get('newsletters_scanned', 0)}")
    print(f"⏰ Generated at: {data.get('generated_at', 'Unknown')}")
    
    if 'research_intelligence' in data and 'error' not in data['research_intelligence']:
        intelligence = data['research_intelligence']['research_intelligence']
        print(f"\n📋 Intelligence Report Preview:")
        print(intelligence[:500] + "..." if len(intelligence) > 500 else intelligence)
    
    if 'outreach_strategy' in data and 'error' not in data['outreach_strategy']:
        print(f"\n📧 Outreach Strategy Generated: ✅")
    
    print("\n" + "="*60)

def quick_scan(target_researchers=None):
    """Quick scan of specific researchers"""
    if target_researchers is None:
        # Focus on top consciousness researchers
        target_researchers = [
            "https://garymarcus.substack.com",
            "https://magazine.sebastianraschka.com", 
            "https://oneusefulthing.substack.com"
        ]
    
    print("🔍 Quick scan mode - checking top researchers...")
    return run_research_intelligence(target_researchers, posts_per_newsletter=2)

def full_sweep():
    """Full intelligence sweep of all newsletters"""
    print("🌊 Full sweep mode - comprehensive intelligence gathering...")
    return run_research_intelligence(ALL_NEWSLETTERS, posts_per_newsletter=4)

if __name__ == "__main__":
    print("🎙️ The Papers That Dream - Research Intelligence System")
    print("="*60)
    
    # Check configuration
    if RUNPOD_API_KEY == "YOUR_RUNPOD_API_KEY" or ENDPOINT_URL == "YOUR_ENDPOINT_URL":
        print("❌ Please configure your RUNPOD_API_KEY and ENDPOINT_URL first!")
        exit(1)
    
    # Choose mode
    print("Choose mode:")
    print("1. Quick scan (3 key researchers)")
    print("2. Full sweep (all 10 newsletters)")
    print("3. Custom list")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        data = quick_scan()
    elif choice == "2":
        data = full_sweep()
    elif choice == "3":
        print("Enter newsletter URLs (one per line, empty line to finish):")
        custom_newsletters = []
        while True:
            url = input().strip()
            if not url:
                break
            custom_newsletters.append(url)
        data = run_research_intelligence(custom_newsletters)
    else:
        print("Invalid choice, running quick scan...")
        data = quick_scan()
    
    if data:
        filename = save_intelligence_report(data)
        print_summary(data)
        print(f"\n📁 Full report saved to: {filename}")
        print("🎯 Ready to identify your next podcast collaboration!")
    else:
        print("❌ No data collected. Check your configuration and try again.")
