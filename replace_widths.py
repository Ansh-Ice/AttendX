import os
import glob

def replace_in_files():
    search_dir = "c:/Users/anshi/OneDrive/Desktop/Projects/AttendX/src"
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                new_content = content.replace("use_container_width=True", "width=\"stretch\"")
                new_content = new_content.replace("use_container_width=False", "width=\"content\"")
                
                if content != new_content:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                        print(f"Updated {path}")

if __name__ == "__main__":
    replace_in_files()
