import subprocess
import sys
import os
from fastapi import FastAPI, HTTPException
from typing import Dict

app = FastAPI(title="Trading System Controller")

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

SCRIPTS = {
    "data_engine": "scripts/data_engine.py",
    "train": "scripts/train.py",
    "live_trader": "scripts/live_trader.py"
}

processes: Dict[str, subprocess.Popen] = {}

@app.on_event("shutdown")
def shutdown_event():
    for proc in processes.values():
        if proc.poll() is None:
            proc.terminate()

@app.post("/start/{script_id}")
async def start_script(script_id: str):
    if script_id not in SCRIPTS:
        raise HTTPException(status_code=404, detail="Script not found")
    
    if script_id in processes and processes[script_id].poll() is None:
        return {"status": "already_running"}

    log_path = os.path.join(LOG_DIR, f"{script_id}.log")
    log_file = open(log_path, "a") # Open in append mode

    proc = subprocess.Popen(
        [sys.executable, "-u", SCRIPTS[script_id]],
        stdout=log_file,
        stderr=subprocess.STDOUT,
        start_new_session=True 
    )
    
    processes[script_id] = proc
    return {"status": "started", "pid": proc.pid}

@app.post("/stop/{script_id}")
async def stop_script(script_id: str):
    if script_id in processes and processes[script_id].poll() is None:
        processes[script_id].terminate()
        return {"status": "stopped"}
    return {"status": "not_running"}

@app.post("/clear_logs/{script_id}")
async def clear_logs(script_id: str):
    """Wipes the content of the log file."""
    log_path = os.path.join(LOG_DIR, f"{script_id}.log")
    if os.path.exists(log_path):
        try:
            # Opening in 'w' mode and immediately closing truncates the file
            with open(log_path, "w") as f:
                f.truncate(0)
            return {"status": "logs_cleared"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return {"status": "no_file_to_clear"}

@app.get("/status")
async def get_status():
    return {name: ("Running" if name in processes and processes[name].poll() is None else "Stopped") 
            for name in SCRIPTS}

@app.get("/logs/{script_id}")
async def get_logs(script_id: str, lines: int = 20):
    log_path = os.path.join(LOG_DIR, f"{script_id}.log")
    if not os.path.exists(log_path):
        return {"logs": "Initializing..."}
    
    try:
        with open(log_path, "r") as f:
            content = f.readlines()
            return {"logs": "".join(content[-lines:])}
    except:
        return {"logs": "Error reading log file."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)