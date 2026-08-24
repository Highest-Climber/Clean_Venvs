import os
import pathlib
import shutil
import subprocess
import sys

def confirm(prompt):
	response = input(prompt).strip().lower()
	if "y" in response and "n" not in response:
		return True
	return False

def find_python(path):
	possible_pythons = [path / "bin" / "python", path / "Scripts" / "python.exe"]
	for possible_python in possible_pythons:
		if possible_python.is_file():
			if subprocess.run([str(possible_python), "-c", "import sys; print(sys.prefix == sys.base_prefix)"], capture_output=True, text=True).stdout.strip() == "False":
				return possible_python
	return None

def process_directory(path, python):
	confirmation = confirm(f"Removing virtual environment at {path}. Would you like to continue? [y/N] ")
	if not confirmation:
		print(f"Skipping virtual environment at {path}.")
		return
	try:
		requirements = subprocess.run([str(python), "-m", "pip", "freeze"], check=True, timeout=60, capture_output=True, text=True)
	except subprocess.CalledProcessError as error:
		print(f"Failed to run pip freeze on virtual environment at {path}.")
		print(f"Error code: {error.returncode}")
		print(f"Error output: {error.stderr}")
		return
	except subprocess.TimeoutExpired:
		print(f"Running pip freeze on virtual environment at {path} took too long.")
		return
	requirements_file = path.parent / "requirements.txt"
	with open(requirements_file, "w") as fout:
		fout.write(requirements.stdout)
	try:
		shutil.rmtree(path)
	except FileNotFoundError:
		pass
	except OSError as error:
		print(f"Failed to remove {path} due to {error}.")
		return
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
