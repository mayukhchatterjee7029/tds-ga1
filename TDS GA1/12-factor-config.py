from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import os
import yaml

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 1. Defaults
config = {"port": 8000, "workers": 1, "debug": False, "log_level": "info", "api_key": "default-secret-000"}

# 2. YAML
try:
    with open("config.development.yaml", "r") as f:
        y = yaml.safe_load(f) or {}
        if "workers" in y: config["workers"] = y["workers"]
        if "debug" in y: config["debug"] = y["debug"]
except FileNotFoundError: pass

# 3. .env
try:
    with open(".env", "r") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                if k == "APP_PORT": config["port"] = int(v)
                elif k == "NUM_WORKERS": config["workers"] = int(v)
                elif k == "APP_API_KEY": config["api_key"] = v
except FileNotFoundError: pass

# 4. OS Env
if "APP_PORT" in os.environ: config["port"] = int(os.environ["APP_PORT"])
if "APP_WORKERS" in os.environ: config["workers"] = int(os.environ["APP_WORKERS"])
if "APP_LOG_LEVEL" in os.environ: config["log_level"] = os.environ["APP_LOG_LEVEL"]
if "APP_API_KEY" in os.environ: config["api_key"] = os.environ["APP_API_KEY"]

def parse_bool(v):
    return str(v).lower() in ("true", "1", "yes", "on")

@app.get("/effective-config")
def get_config(set: list[str] = Query(default=[])):
    res = {
        "port": int(config["port"]),
        "workers": int(config["workers"]),
        "debug": parse_bool(config["debug"]),
        "log_level": str(config["log_level"]),
        "api_key": "****" # Always masked
    }
    # 5. Query params (highest precedence)
    for item in set:
        if "=" in item:
            k, v = item.split("=", 1)
            if k == "port": res["port"] = int(v)
            elif k == "workers": res["workers"] = int(v)
            elif k == "debug": res["debug"] = parse_bool(v)
            elif k == "log_level": res["log_level"] = str(v)
            elif k == "api_key": res["api_key"] = "****"
    return res