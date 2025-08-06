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

See `example.py` for some basic examples and `more_examples.py` for examples on how to use imports in the code.

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

# Assign a dynamic port number to prevent conflicts when multiple jobs are executed on the same node.
# The port number is derived using SLURM_JOB_ID to ensure uniqueness within the node.
PORT=$((1729 + (SLURM_JOB_ID % 100)))
echo "Using port: $PORT for job $SLURM_JOB_ID"

module purge
module load apptainer 

# Start uvicorn server in background
echo "Starting uvicorn server on port $PORT..."
apptainer exec \
   --writable-tmpfs \
   sandbox_for_llm_code.sif \
   bash -c "cd /app && export LOG_FILE=/tmp/app.log && uvicorn main:app --host 0.0.0.0 --port $PORT" > /ptmp/$USER/slurm_jobs/uvicorn.${SLURM_JOB_ID}.log 2>&1 &
APPTAINER_PID=$!
echo "Started apptainer process: $APPTAINER_PID"

# Wait a moment for uvicorn to start inside container
sleep 3

# Check if apptainer process is still running
if ! kill -0 $APPTAINER_PID 2>/dev/null; then
   echo "ERROR: Apptainer process died unexpectedly"
   echo "Check uvicorn logs: /ptmp/$USER/slurm_jobs/uvicorn.${SLURM_JOB_ID}.log"
   exit 1
fi
echo "Apptainer process is running: $APPTAINER_PID"

# Wait for uvicorn to be ready to accept requests
echo "Waiting for uvicorn server to be ready..."
max_attempts=30
attempt=0
server_ready=false

while [ $attempt -lt $max_attempts ] && [ "$server_ready" = false ]; do
   attempt=$((attempt + 1))
   echo "Attempt $attempt/$max_attempts: Checking if server is ready..."
   
   # Check if apptainer process is still running
   if ! kill -0 $APPTAINER_PID 2>/dev/null; then
      echo "ERROR: Apptainer process died unexpectedly"
      echo "Check uvicorn logs: /ptmp/$USER/slurm_jobs/uvicorn.${SLURM_JOB_ID}.log"
      exit 1
   fi
   
   # Check if port is listening
   if netstat -tuln | grep -q ":${PORT} "; then
      echo "Port ${PORT} is listening"
      
      # Test if the server actually responds
      if curl -s --max-time 5 http://localhost:${PORT}/execute_code/ -X POST -H "Content-Type: application/json" -d '{"code": "print(\"test\")", "local_dict": {}}' >/dev/null 2>&1; then
            echo "SUCCESS: Uvicorn server is ready and responding to requests!"
            server_ready=true
      else
            echo "Port is listening but server not responding yet..."
      fi
   else
      echo "Port ${PORT} not yet listening..."
   fi
   
   if [ "$server_ready" = false ]; then
      sleep 2
   fi
done

if [ "$server_ready" = false ]; then
   echo "ERROR: Uvicorn server failed to start within $((max_attempts * 2)) seconds"
   echo "Apptainer process status:"
   ps aux | grep $APPTAINER_PID
   echo "Port status:"
   netstat -tuln | grep ${PORT}
   echo "Available ports:"
   netstat -tuln | grep LISTEN
   exit 1 # kill this job
fi

echo "Uvicorn server is ready and running on port ${PORT}"

# YOUR SCRIPT GOES HERE --> Pass the port endpoint with the correct port here. 
python example.py  code_execution_endpoint=http://localhost:${PORT}/execute_code/

# Capture the exit status of the Python command
PYTHON_EXIT_STATUS=$?

echo "Python command completed with exit status: $PYTHON_EXIT_STATUS"

# Clean up apptainer when done (only if it was started)
if [ "$NEED_CODE_EXECUTION" = true ] && [ ! -z "$APPTAINER_PID" ]; then
    echo "Stopping apptainer process (PID: $APPTAINER_PID)..."
    kill $APPTAINER_PID 2>/dev/null || true
fi

# Exit with the same status as the Python command
# This tells SLURM whether the job succeeded (0) or failed (non-zero)
echo "Job completed. Exiting with status: $PYTHON_EXIT_STATUS"
exit $PYTHON_EXIT_STATUS
```

## Acknowledgements
This project is greatly helped by Cursor IDE and the method shared in the [Medium Article](https://medium.com/@Shrishml/making-our-own-code-interpreter-part-1-making-of-a-sandbox-382da3339eaa).
