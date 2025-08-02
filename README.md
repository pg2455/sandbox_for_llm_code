# Sandbox for LLM Code

Running code output by LLMs carries security risks. As a result, we need a sandbox environment isolated from our main environment.

This repo contains minimal code to create that environment. It is a FastAPI-based sandbox that allows you to execute Python code through API calls.

Fork, clone, and modify as you wish.

**How I use it?** This is a minimal environment that I use for my research projects involving LLM code.

## Quick Start

### Prerequisites
- Docker installed on your system
- Port 1729 available (or modify the port in the Dockerfile)

### Clone this repo

```bash
git clone https://github.com/pg2455/sandbox_for_llm_code.git
```

### Building and Running

1. **Build the Docker image:** Make sure Docker is running. 
   ```bash
   cd sandbox_for_llm_code
   docker build -t code-sandbox .
   ```

2. **Run the container:**
   ```bash
   docker run -p 1729:1729 code-sandbox
   ```

3. **Access the API from your code:**
   API Base URL: `http://0.0.0.0:1729`
   
   **Available Endpoints:**
   - `POST /execute_code/` - Execute Python code with local variables

## Examples

See `example.py` for some examples.

## Extension

To add more functionality to the sandbox, you can create additional POST and GET endpoints. For example, 

- **File Upload**: Add a POST endpoint to upload CSV files and save them in `global_dict`
- **File Download**: Add a POST endpoint to download files or results
- **Persistent Storage**: Implement file system access for data persistence
- **Custom Libraries**: Add support for additional Python packages
- **Execution Limits**: Implement timeout and memory usage limits
- **Logging**: Add comprehensive execution logging

#### Example Extension Structure:
```python
@app.post("/upload_file/")
async def upload_file(file: UploadFile):
    # Handle file upload logic
    pass

@app.get("/download_result/{result_id}")
async def download_result(result_id: str):
    # Handle file download logic
    pass
```

## How to push to DockerHub for SLURM usage?

### 1. Determine the architecture
First, determine the architecture of your server nodes (Intel x86_64 or AMD aarch64). You can do this by executing `lscpu` on the node and checking the `Architecture` field.

### 2. Create a DockerHub Account
If you don't have one, create an account at [DockerHub](https://hub.docker.com/)

### 3. Login to DockerHub
```bash
docker login
# Enter your DockerHub username and password/token
```

### 4. Build and push the Docker image for your node architecture
```bash
# Enable buildx for multi-platform builds
docker buildx create --name sandbox_for_llm_code --use

# Replace 'your-dockerhub-username' with your actual DockerHub username
# For x86_64 nodes:
docker buildx build --platform linux/amd64 -t your-dockerhub-username/sandbox_for_llm_code:latest . --push

# For ARM64 nodes:
docker buildx build --platform linux/arm64 -t your-dockerhub-username/sandbox_for_llm_code:latest . --push

# Or build for multiple platforms:
docker buildx build --platform linux/amd64,linux/arm64 -t your-dockerhub-username/sandbox_for_llm_code:latest . --push
```

## How to launch this server on SLURM?

### 1. Make the Apptainer version available on the login node
Apptainer doesn't require root privileges, which is why it's widely used on SLURM servers instead of Docker.

```bash
# On the login node
module load apptainer            # or singularity
apptainer build --sandbox sandbox_for_llm_code.sif docker://your-dockerhub-username/sandbox_for_llm_code:latest
```

This step downloads the Docker image from the registry, squashes it into a single, read-only SIF image, and makes it available to run.

### 2. Launch the Apptainer version in your SLURM script

```bash
#!/bin/bash
#SBATCH -N 1
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH -J code-sandbox-test

module load apptainer

echo "Starting uvicorn server..."
apptainer exec \
    --writable-tmpfs \
    sandbox_for_llm_code.sif \
    bash -c "cd /app && export LOG_FILE=/tmp/app.log && uvicorn main:app --host 0.0.0.0 --port 1729" &
UVICORN_PID=$!

echo "Checking uvicorn status..."
ps aux | grep uvicorn
netstat -tuln | grep 1729

sleep 5                          # give the server a moment
python example.py                # talks to http://0.0.0.1:1729

# Clean up uvicorn when done
if [ ! -z "$UVICORN_PID" ]; then
    echo "Stopping uvicorn server..."
    kill $UVICORN_PID
fi
```

## Acknowledgements
This project is greatly helped by Cursor IDE and the method shared in the [Medium Article](https://medium.com/@Shrishml/making-our-own-code-interpreter-part-1-making-of-a-sandbox-382da3339eaa).
