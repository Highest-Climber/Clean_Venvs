import os
import pathlib
import re
import subprocess
import sys

yes_pattern = re.compile(r"(?i)\b(y|yes|yeah|yep|yup|sure|ok(?:ay)?|alright|affirmative|correct|true|indeed|absolutely|definitely|of course|sounds good|why not|i think so|i guess so)\b")
no_pattern = re.compile(r"(?i)\b(n|no|nope|nah|naw|negative|never|false|incorrect|not really|not at all|absolutely not|do not|don't|cannot|can't|won't)\b")

def read_yes_no(prompt):
    while True:
        response = input(prompt)
        if yes_pattern.search(response) and not no_pattern.search(response):
            return True
        elif no_pattern.search(response) and not yes_pattern.search(response):
            return False
        else:
            print("I didn't understand that.")

def find_python(path):
	possible_pythons = [path / "bin" / "python", path / "Scripts" / "python.exe"]
	for possible_python in possible_pythons:
		if possible_python.is_file():
			if subprocess.run([str(possible_python), "-c", "import sys; print(sys.prefix == sys.base_prefix)"], capture_output=True, text=True).stdout.strip() == "False":
				return possible_python
	return None

def process_directory(path, python):
	confirmation = read_yes_no(f"Removing virtual environment at {path}. Would you like to continue? ")
	if not confirmation:
		print(f"Skipping virtual environment at {path}.")
		return
	try:
		requirements = subprocess.run([str(python), "-m", "pip", "freeze"], check=True, timeout=60, capture_output=True, text=True)
	except subprocess.CalledProcessError:
		print(f"Failed to run pip freeze on virtual environment at {path}.")
		print(f"Error code: {requirements.returncode}")
		print(f"Error output: {requirements.stderr}")
		return
	except subprocess.TimeoutExpired:
		print(f"Running pip freeze on virtual environment at {path} took too long.")
		return
	requirements_file = path.parent / "requirements.txt"
	with open(requirements_file, "w") as fout:
		fout.write(requirements.stdout)
	subprocess.run(["rm", "-rf", path])
	print(f"Sucessfully wrote requirements.txt file and deleted virtual environment at {path}.")
	return

def clean_up(root):
	for current, directories, files in os.walk(root):
		path = pathlib.Path(current)
		if "pyvenv.cfg" not in files:
			continue
		python = find_python(path)
		if python is None:
			continue
		directories.clear()
		process_directory(path, python)

if __name__ == "__main__":
	if len(sys.argv) > 1:
		for i in range(1, len(sys.argv)):
			try:
				root = pathlib.Path(sys.argv[i]).resolve(strict=True)
			except FileNotFoundError:
				print(f"Could not resolve {sys.argv[i]}. Continuing to the next argument...")
				continue
			clean_up(root)
	else:
		clean_up(pathlib.Path.cwd())
