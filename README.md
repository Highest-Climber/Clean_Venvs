# Clean_Venvs

## Description
This Python script automatically finds all Python virtual environments and replaces it with a `requirements.txt` file.

## Usage
With no arguments, the script will recursively search all directories in your current directory for Python virtual environments. Run it like so:
```bash
python3 clean_venvs.py
```
With arguments, just specify the directories you would like to have searched recursively. Run it like so:
```bash
python3 clean_venvs.py directory1/ /home/your_name/
```