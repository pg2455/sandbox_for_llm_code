# Sandbox for LLM Code

Running code output by LLMs carries security risks. As a result, we need a sandbox environment isolated from our main environment.

This repo contains minimal code to create that environment. It is a FastAPI-based sandbox that allows you to execute Python code through API calls.

Fork, clone, and modify as you wish.

**How I use it?:** This is a minimal environment that I use for my research projects involving LLM code.

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