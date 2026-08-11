import subprocess
import os

def run_cmd(cmd):
    print(f"Running: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print("STDOUT:", res.stdout)
    if res.stderr:
        print("STDERR:", res.stderr)
    return res.stdout.strip()

if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    os.chdir(PROJECT_ROOT)

    # 1. Update .gitignore to exclude large media files (>50MB) and zip files
    gitignore_path = os.path.join(PROJECT_ROOT, ".gitignore")
    with open(gitignore_path, "a") as f:
        f.write("\n\n# Large media & animation files >50MB\n")
        f.write("booking/static/images/aianimation2\n")
        f.write("*.zip\n")
        f.write("ghidora_payments_fixed.zip\n")
        f.write("ghidora_social_app.zip\n")

    print("Updated .gitignore.")

    # 2. Reset last commit softly to unstage the 320MB file
    run_cmd("git reset --soft HEAD~1")

    # 3. Unstage large files from git tracking
    run_cmd("git rm --cached -f booking/static/images/aianimation2")
    run_cmd("git rm --cached -f ghidora_payments_fixed.zip")
    run_cmd("git rm --cached -f ghidora_social_app.zip")

    # 4. Stage all valid code files
    run_cmd("git add .")

    # 5. Commit clean codebase
    run_cmd('git commit -m "Upgrade Smart Occasions System, 3D HD Buttons, GPS Engine, and Quotations (clean)"')

    print("Ready to push!")
