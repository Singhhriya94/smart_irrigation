import os
import time
import requests
import subprocess
from openai import OpenAI
from client import SmartIrrigationEnv
from models import IrrigationAction

def agent_action(llm_client, obs, model_name):
    prompt = (
        f"You are managing a smart irrigation system.\n"
        f"Day: {obs.day}\nSoil Moisture: {obs.soil_moisture:.2f} (optimal 0.4-0.7)\n"
        f"Temperature: {obs.temperature:.2f}C\nRained Today: {obs.has_rained}\n"
        f"Return an action: 0 (None), 1 (Low), 2 (Medium), 3 (High).\n"
        f"Return ONLY the single integer."
    )
    try:
        response = llm_client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10
        )
        ans = response.choices[0].message.content.strip()
        # extract just the number
        ans = ''.join(filter(str.isdigit, ans))
        if ans in ['0', '1', '2', '3']:
            return int(ans)
        return 0
    except Exception as e:
        # Fallback to a dumb heuristic if API fails or is not configured
        if obs.soil_moisture < 0.4:
            return 3
        elif obs.soil_moisture > 0.7:
            return 0
        return 1

def run_simulation():
    # Start the server locally
    print("Starting FastAPI server...")
    server_process = subprocess.Popen(["uvicorn", "server.app:app", "--port", "8000"])
    time.sleep(3)  # wait for server to start up

    base_url = "http://localhost:8000"
    
    # Initialize OpenAI client using Proxy values as per guidelines
    api_base = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
    api_key = os.environ.get("API_KEY", "dummy_key")
    llm_client = OpenAI(base_url=api_base, api_key=api_key)
    
    model_name = os.environ.get("DEFAULT_MODEL", "Qwen/Qwen2.5-72B-Instruct")

    try:
        # Get tasks from server
        tasks = requests.get(f"{base_url}/tasks").json()
        
        for task in tasks:
            print(f"[START] task={task}, env=smart-irrigation, model={model_name}")
            with SmartIrrigationEnv(base_url=base_url).sync() as env:
                res = env.reset()
                obs = res.observation
                done = False
                steps = 0
                
                while not done:
                    action_val = agent_action(llm_client, obs, model_name)
                    action = IrrigationAction(action=action_val)
                    res = env.step(action)
                    obs = res.observation
                    done = res.done
                    reward = res.reward
                    steps += 1
                    
                    print(f"[STEP] step={steps} reward={reward:.2f} done={done} action={action_val}")
                    
                # get score using the 0.05-0.95 scaling endpoint
                score_data = requests.get(f"{base_url}/scale_score?health={obs.crop_health}").json()
                score = score_data.get("security_score", 0.0)
                print(f"[END] task={task} score={score:.4f} steps={steps}")
                
    except Exception as e:
        print(f"Simulation failed: {e}")
    finally:
        server_process.terminate()

if __name__ == "__main__":
    run_simulation()
