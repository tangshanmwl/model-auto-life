import os
import json
import random
import requests
import sys
import datetime

def get_configs():
    configs = []
    
    # Try to read from API_CONFIGS (JSON list)
    api_configs_env = os.environ.get('API_CONFIGS')
    if api_configs_env:
        try:
            configs = json.loads(api_configs_env)
            if not isinstance(configs, list):
                print("Error: API_CONFIGS must be a JSON list.")
                configs = []
        except json.JSONDecodeError as e:
            print(f"Error parsing API_CONFIGS: {e}")
    
    # If no configs from JSON, try individual env vars
    if not configs:
        url = os.environ.get('API_URL')
        token = os.environ.get('API_TOKEN')
        model = os.environ.get('MODEL_NAME')
        
        if url and token and model:
            configs.append({
                "url": url,
                "token": token,
                "model": model
            })
            
    return configs

def generate_math_question():
    a = random.randint(0, 100)
    b = random.randint(0, 100)
    operator = random.choice(['+', '-'])
    
    if operator == '+':
        question = f"{a}+{b}等于多少"
    else:
        # Avoid negative numbers for simplicity, though not strictly required
        if a < b:
            a, b = b, a
        question = f"{a}-{b}等于多少"
        
    return question

def write_log(question, result):
    # Use UTC+8 (Beijing Time)
    utc_now = datetime.datetime.utcnow()
    beijing_time = utc_now + datetime.timedelta(hours=8)
    timestamp = beijing_time.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(base_dir, "log.txt")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"请求时间：[{timestamp}]\n")
            f.write(f"请求内容：{question}\n")
            f.write(f"请求结果：{result}\n\n")
    except Exception as e:
        print(f"Error writing to log: {e}")

def send_request(config):
    url = config.get('url')
    token = config.get('token')
    model = config.get('model')
    
    if not url or not token or not model:
        print(f"Skipping invalid config: {config}")
        return

    question = generate_math_question()
    print(f"Sending request to {url} with model {model}...")
    print(f"Question: {question}")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ],
        "temperature": 0.8,
        "max_tokens": 1000
    }
    
    result_log = ""
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                resp_json = response.json()
                # User specifically asked for choices[0].message.content
                choices = resp_json.get('choices', [])
                if choices and len(choices) > 0:
                    message = choices[0].get('message', {})
                    content = message.get('content', '')
                    result_log = content
                else:
                    # Fallback if structure is different but status is 200
                    result_log = f"Success (200) but unexpected JSON structure: {response.text[:200]}"
            except Exception as e:
                # JSON parse error
                result_log = f"Success (200) but failed to parse JSON: {response.text[:200]}"
        else:
            # Non-200
            result_log = f"Request failed. Status: {response.status_code}. Response: {response.text[:200]}"
            print("Request failed!")
            
    except Exception as e:
        result_log = f"Request exception: {str(e)}"
        print(f"Error sending request: {e}")

    # Always write log
    print(f"Result to log: {result_log[:100]}...")
    write_log(question, result_log)

def main():
    configs = get_configs()
    
    if not configs:
        print("No configurations found. Please set API_CONFIGS or (API_URL, API_TOKEN, MODEL_NAME).")
        sys.exit(1)
        
    print(f"Found {len(configs)} configuration(s).")
    
    for i, config in enumerate(configs):
        print(f"\n--- Processing Config {i+1} ---")
        send_request(config)

if __name__ == "__main__":
    main()
