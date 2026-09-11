#!/usr/bin/env python3
"""
LexiMini AI — Standalone Live Demo Runner
Launches Gateway (8000), RAG Engine (8001), Model Server (8002), and React Enterprise Web UI (3000).
"""

import subprocess
import sys
import time
import os

def start_services():
    print("=================================================================")
    print("       ⚖️ LexiMini AI — Indian Legal Assistant Platform        ")
    print("=================================================================\n")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(base_dir)

    processes = []

    env = os.environ.copy()
    env["GATEWAY_URL"] = "http://localhost:8000"
    env["RAG_SERVICE_URL"] = "http://localhost:8001"
    env["MODEL_SERVER_URL"] = "http://localhost:8002"

    try:
        print("[1/4] Starting FastAPI API Gateway on http://localhost:8000...")
        p_gateway = subprocess.Popen([sys.executable, "-m", "uvicorn", "services.gateway.main:app", "--port", "8000", "--host", "0.0.0.0"], env=env)
        processes.append(p_gateway)

        print("[2/4] Starting Hybrid RAG Engine on http://localhost:8001...")
        p_rag = subprocess.Popen([sys.executable, "-m", "uvicorn", "services.rag_engine.main:app", "--port", "8001", "--host", "0.0.0.0"], env=env)
        processes.append(p_rag)

        print("[3/4] Starting Model Server Engine on http://localhost:8002...")
        p_model = subprocess.Popen([sys.executable, "-m", "uvicorn", "services.model_server.main:app", "--port", "8002", "--host", "0.0.0.0"], env=env)
        processes.append(p_model)

        time.sleep(2)
        print("[4/4] Starting React Enterprise Web App on http://localhost:3000...")
        p_web = subprocess.Popen(["npm", "--prefix", "apps/web", "run", "dev"], env=env)
        processes.append(p_web)

        print("\n[Success] All LexiMini AI Microservices are live!")
        print("  - React Web UI:     http://localhost:3000")
        print("  - API Gateway Docs: http://localhost:8000/docs")
        print("  - RAG Engine Docs:  http://localhost:8001/docs")
        print("  - Model Server:     http://localhost:8002/docs")
        print("\nPress Ctrl+C to terminate all services safely.\n")

        for p in processes:
            p.wait()

    except KeyboardInterrupt:
        print("\n[Shutdown] Terminating all microservices safely...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.wait()
        print("[Shutdown] Completed.")

if __name__ == "__main__":
    start_services()
