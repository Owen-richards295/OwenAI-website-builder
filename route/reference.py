import os

REFERENCE = "index.html"
def load_reference():
	if not os.path.exists(REFERENCE):
		return f"NO such file named {REFERENCE} continuing with the designs without reference"
	with open(REFERENCE, "r", encoding="utf-8") as file:
		return file.read()
REFERENCE_DESIGN = load_reference()