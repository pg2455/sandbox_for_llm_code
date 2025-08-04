import requests 

def demonstrate_successful_execution():
    """
    Demonstrates successful code execution using the API.
    Shows how to execute valid code with proper local variables.
    """
    url = "http://localhost:1729"
    
    print("=== Successful Code Execution Examples ===\n")
    
    # Example 1: Basic arithmetic
    print("Example 1: Basic arithmetic")
    print("Code: out=x+y")
    print("Local variables: x=10, y=2")
    
    payload = {
        "code": "out=x+y",
        "local_dict": {
            "x": 10,
            "y": 2
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

def demonstrate_error_handling():
    """
    Demonstrates error handling in code execution using the API.
    Shows what happens when code contains errors or undefined variables.
    """
    url = "http://localhost:1729"  # Use localhost for consistency
    
    print("=== Error Handling Examples ===\n")
    
    # Example 1: Undefined variable
    print("Example 1: Undefined variable")
    print("Code: out=b")
    print("Local variables: x=10, y=2 (but 'b' is not defined)")
    
    payload = {
        "code": "out=b",
        "local_dict": {
            "x": 10,
            "y": 2
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
    demonstrate_successful_execution()
    demonstrate_error_handling()


