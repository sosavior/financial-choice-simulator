import os

output_file = "core_architecture.txt"
# Only scanning the folders containing your actual logic
target_dirs = ["src", "tests"] 
extensions = [".py"]

with open(output_file, "w", encoding="utf-8") as outfile:
    for d in target_dirs:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            # Skip cache directories
            if "__pycache__" in root:
                continue
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    path = os.path.join(root, file)
                    outfile.write(f"\n\n{'='*80}\n/// FILE: {path} ///\n{'='*80}\n\n")
                    try:
                        with open(path, "r", encoding="utf-8") as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"Error reading file: {e}\n")

print(f"Success. All core logic has been compiled into {output_file}")