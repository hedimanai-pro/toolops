import os
import re

def remove_unused_ignores(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                
                new_lines = []
                for line in lines:
                    # Remove "  # type: ignore" or " # type: ignore"
                    new_line = re.sub(r'\s+#\s+type:\s+ignore(\[.*\])?', '', line.rstrip())
                    new_lines.append(new_line + "\n")
                
                with open(path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)

# Run on toolops and tests
remove_unused_ignores("toolops")
remove_unused_ignores("tests")
print("Done removing ignores.")
