import subprocess
import time
import sys
import os

def get_base_dir():
    if getattr(sys, 'frozen', False):
        # Estamos rodando como .exe (PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # Estamos rodando como script .py
        return os.path.dirname(os.path.abspath(__file__))

def run_backend(base_dir):
    print("Iniciando backend (API)...")
    src_path = os.path.join(base_dir, "src")
    command = [sys.executable, "-m", "uvicorn", "api:app", "--port", "8000"]
    
    # Só usa --reload se estiver rodando em modo de desenvolvimento
    if not getattr(sys, 'frozen', False):
        command.append("--reload")
    
    return subprocess.Popen(command, cwd=src_path)


def run_frontend(base_dir):
    print("Iniciando frontend (Flet)...")
    subprocess.run([sys.executable, os.path.join(base_dir, "src", "app.py")])

if __name__ == "__main__":
    base_dir = get_base_dir()
    backend = run_backend(base_dir)
    time.sleep(3)
    try:
        run_frontend(base_dir)
    finally:
        print("Encerrando backend...")
        backend.terminate()
