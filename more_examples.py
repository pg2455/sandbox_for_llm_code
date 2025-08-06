import requests

def create_simple_sum_function() -> str:
    """
    Creates a simple sum function that demonstrates the concept.
    """
    return '''
from typing import Any
def simple_sum_with_random(a: float, b: float) -> Any:
    """
    Simple function that adds two numbers and adds a random small value.
    Requires 'random' library to be imported.
    """
    import random
    
    base_sum = a + b
    random_addition = random.uniform(-0.5, 0.5)
    return base_sum + random_addition

c = simple_sum_with_random(a, b)
'''

def demonstrate_function_execution():
    """
    Demonstrates error handling in code execution using the API.
    Shows what happens when code contains errors or undefined variables.
    """
    url = "http://localhost:1729"  # Use localhost for consistency
    
    
    # Example 1: Undefined variable
    print("Example 1: Simple sum")
    code_string = create_simple_sum_function()

    payload = {
        "code": code_string,
        "local_dict": {
            "a": 10,
            "b": 2
        }
    }
    
    try:
        response = requests.post(f'{url}/execute_code/', json=payload, timeout=10)
        result = response.json()
        print(f"Result: {result}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused - server not running")
    except requests.exceptions.Timeout:
        print("❌ Request timeout - server not responding")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "-"*50 + "\n")


if __name__ == "__main__":
    demonstrate_function_execution()