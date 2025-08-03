from fastapi import FastAPI, HTTPException
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
from io import BytesIO
import pandas as pd
import json 
import traceback
import utils
import logging

# Setup colored logging
utils.setup_colored_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

global_dict = {}

@app.post("/execute_code/")
async def execute_code(request_body: dict):
    """Executes the code in the request_body. 
    
    Args:
        request_body (dict): Must include `code` as the key which is executed. 
            Additional variables can be provided through `local_dict`. 
    Returns:
        Returns the output of the code in JSON format, or error details if execution fails.
    """
    
    local_dict = request_body.get('local_dict', {})
    code = request_body.get('code')
    
    # no code
    if not code:
        logger.warning("No code provided in request")
        return JSONResponse(
            status_code=400,
            content={'error': 'No code provided in request body'}
        )

    logger.info(f"📝 Code:\n{utils.add_line_numbers(code)}")
    logger.info(f"📦 Local variables:\n{local_dict}")
    logger.info("Executing code request...")

    try:

        exec(code, global_dict, local_dict)
        logger.info("🐍 Code executed successfully")
        remove_keys = []
        for key, value in local_dict.items():
            if not utils.is_json_serializable(value):
                remove_keys.append(key)

        _ = [local_dict.pop(key) for key in remove_keys]
        return JSONResponse(content={'result': local_dict, 'success': True})
    except Exception as e:
        try:
            error_info = {
                'error': str(e),
                'error_type': type(e).__name__,
                'traceback': traceback.format_exc(),
                'success': False
            }
            logger.error(f"❌ Code execution failed: {type(e).__name__}: {str(e)}")
            logger.error(f"Traceback: {error_info['traceback']}")
            return JSONResponse(
                status_code=400,
                content=error_info
            )
        except Exception as handler_error:
            # Fallback error response if error handling itself fails
            logger.error(f"Error handler failed: {handler_error}")
            return JSONResponse(
                status_code=500,
                content={
                    'error': 'Internal server error during error handling',
                    'original_error': str(e),
                    'success': False
                }
            )