import os
import glob
import subprocess
import json
import time
import sys

FOLDER = "/home/opc/Main/Facebook"
PROMPT = "Upscale to 4K resolution, significantly improve sharpness and clarity, remove jpeg artifacts, and enhance details for a professional look."
LOG_FILE = "/home/opc/Main/Facebook/process_images.log"

# Use absolute path to image-tool
IMAGE_TOOL_PATH = "/home/opc/.local/bin/image-tool"

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    print(entry, flush=True)  # Ensure stdout flushes
    try:
        with open(LOG_FILE, "a") as f:
            f.write(entry + "\n")
            f.flush() # Ensure file write flushes
    except Exception as e:
        print(f"Failed to write to log file: {e}", file=sys.stderr)

def process_image(filepath):
    filename = os.path.basename(filepath)
    name_no_ext = os.path.splitext(filename)[0]
    output_path = os.path.join(FOLDER, f"{name_no_ext}-enhanced.png")
    
    if os.path.exists(output_path):
        log(f"Skipping {filename} (already enhanced)")
        return

    log(f"Processing {filename}...")
    
    try:
        # Check if executable exists
        if not os.path.exists(IMAGE_TOOL_PATH):
             log(f"Error: image-tool not found at {IMAGE_TOOL_PATH}")
             return

        # Construct JSON for image-tool edit
        payload = {
            "file": filepath,
            "prompt": PROMPT,
            "size": "auto"
        }
        
        # Run image-tool command using absolute path
        cmd = [IMAGE_TOOL_PATH, "edit", "--json", json.dumps(payload)]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            log(f"Error processing {filename}: {result.stderr}")
            return

        try:
            output_json = json.loads(result.stdout)
            if output_json.get("ok"):
                temp_output = output_json["data"]["image"]
                # Move/Rename to final location
                os.rename(temp_output, output_path)
                log(f"Successfully enhanced {filename} -> {os.path.basename(output_path)}")
            else:
                log(f"Tool error for {filename}: {output_json.get('error')}")
        except json.JSONDecodeError:
             log(f"Invalid JSON output for {filename}: {result.stdout}")

    except Exception as e:
        log(f"Exception processing {filename}: {str(e)}")

def main():
    log("Starting batch image enhancement...")
    images = glob.glob(os.path.join(FOLDER, "*.jpg"))
    images.sort()
    
    count = 0
    total = len(images)
    
    if not images:
        log("No jpg images found in folder.")
        return

    for img in images[:1]: # Limit to 1 for test
        process_image(img)
        count += 1
        # Optional: Add small delay to be nice to API
        time.sleep(2)

    log(f"Batch processing complete. Processed {count}/{total} images.")

if __name__ == "__main__":
    main()
