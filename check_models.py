import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get your API token
HF_API_KEY = os.getenv('HF_API_KEY')

def check_model_access():
    """Check access to specific models and list available ones."""
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    # List of models to check
    models_to_check = [
        "facebook/bart-large-cnn",
        "gpt2",
        "bert-base-uncased",
        "t5-base",
        "distilbert-base-uncased"
    ]
    
    print("\nChecking model access...")
    print("-" * 80)
    
    for model_id in models_to_check:
        try:
            # Try to get model info
            response = requests.get(
                f"https://api-inference.huggingface.co/models/{model_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                model_info = response.json()
                print(f"\nModel: {model_id}")
                print(f"Status: Available")
                print(f"Task: {model_info.get('pipeline_tag', 'Unknown')}")
                print(f"Description: {model_info.get('description', 'No description')[:100]}...")
            else:
                print(f"\nModel: {model_id}")
                print(f"Status: Not available (Status code: {response.status_code})")
                print(f"Error: {response.text}")
            
            print("-" * 80)
            
        except Exception as e:
            print(f"\nError checking model {model_id}: {str(e)}")
            print("-" * 80)

if __name__ == "__main__":
    if not HF_API_KEY:
        print("Error: HF_API_KEY not found in .env file")
    else:
        check_model_access() 