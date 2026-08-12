import subprocess
import sys

def run_cmd(cmd):
    print(f"⚡ Running: {cmd}")
    subprocess.run(cmd, shell=True)

def main():
    commit_msg = sys.argv[1] if len(sys.argv) > 1 else "Auto-sync localhost code and features to Render"
    print("\n=========================================================")
    print("🚀 GHIDORA TRANSPORT — AUTOMATIC LOCALHOST ➔ RENDER DEPLOYER")
    print("=========================================================\n")
    
    print("1️⃣ Staging all localhost code changes...")
    run_cmd("git add .")

    print("2️⃣ Creating commit...")
    run_cmd(f'git commit -m "{commit_msg}"')

    print("3️⃣ Pushing to GitHub (Triggers Render Auto-Deploy)...")
    run_cmd("git push origin main")

    print("\n=========================================================")
    print("✅ SUCCESS! Localhost is now 100% synced with Render!")
    print("🌐 Live Render URL: https://ghidoratransport.onrender.com/")
    print("=========================================================\n")

if __name__ == "__main__":
    main()
