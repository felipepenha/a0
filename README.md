# Agent Zero

## Prerequisites & Requirements

Before running the launcher commands, ensure your environment meets the following requirements:

* **Podman** (or Docker): Required to build and run container images (`agent-zero-local:ready`, `bkimminich/juice-shop`). Check: `podman --version`
* **Ollama** (Required for `make ollama`): Required for offline/local LLM execution without cloud API keys. Download: [https://ollama.com](https://ollama.com) (or `brew install ollama`). Check: `ollama --version`
* **Python 3.10+ & uv**: Required for host automation scripts (`prompt.py`). Managed via `pyproject.toml` and `uv`.
* **Make**: Required for executing Makefile shortcuts (`make run`, `make ollama`, `make attack`).

---

## Running Agent Zero & Data Persistence

### Launching the Container

> [!NOTE]
> These launch targets are **independent and mutually exclusive**. You do **not** run them in sequence. Simply choose **one** command to run based on your desired use case. Each target automatically cleans up previous containers before launching its own environment.

#### 1. Standard Standalone Run (`make run`)

Launches the patched Agent Zero container bound to port `8080`:

```bash
make run
```
* **URL:** `http://localhost:8080`

#### 2. Local Ollama LLM Integration (`make ollama`)

Starts a background Ollama server, verifies model availability (`gpt-oss:20b`), dynamically resolves network gateway routing, and launches Agent Zero bound to port `50001`:

```bash
make ollama
```
* **URL:** `http://localhost:50001`

#### 3. Security Audit Sandbox (`make attack`)

Creates an isolated bridge network (`sec_test_net`), deploys OWASP Juice Shop (`bkimminich/juice-shop` on port `8080`), and starts Agent Zero on port `50001` configured with Option 2 (passive security header & metadata inspection):

```bash
make attack
```
* **Juice Shop Target URL:** `http://localhost:8080`
* **Agent Zero UI:** `http://localhost:50001`
* **Option 2 Prompt:** Inspects HTTP response headers (CSP, HSTS, X-Frame-Options), `robots.txt`, and `sitemap.xml` passively at `http://vulnerable_container:3000`.

### How Data Persistence Works

The container mounts the local host directory `./usr` to `/a0/usr` inside the container (`-v "$(pwd)/usr:/a0/usr:Z"`). This ensures that all session data and configurations are preserved across container restarts, stops, and rebuilds:

* **Settings & Credentials:** `usr/.env`, `usr/settings.json`, `usr/secrets.env`
* **Skills & Knowledge:** `usr/skills/`, `usr/knowledge/`, `usr/memory/` (vector databases)
* **Projects & Workspaces:** `usr/projects/`, `usr/workdir/`
* **Session & Chat History:** `usr/chats/`, `usr/uploads/`, `usr/downloads/`

The `./usr/` directory is listed in `.gitignore` by default to prevent committing credentials or personal session history.

---

## Agent Zero Connectivity Guide

This guide covers the different ways to connect to Agent Zero from external applications, including using the External API, connecting as an MCP client, and enabling agent-to-agent communication.

**Note:** You can find your specific URLs and API tokens in your Agent Zero instance under `Settings > External Services`.

### API Token Information

The API token is automatically generated from your username and password. This same token is used for External API endpoints, MCP server connections, and A2A communication. The token will change if you update your credentials.

---

### External API Endpoints

Agent Zero provides external API endpoints for integration with other applications. These endpoints use API key authentication and support text messages and file attachments.

#### `POST /api_message`

Send messages to Agent Zero and receive responses. Supports text messages, file attachments, and conversation continuity.

##### API Reference

**Parameters:**
*   `context_id` (string, optional): Existing chat context ID
*   `message` (string, required): The message to send
*   `attachments` (array, optional): Array of `{filename, base64}` objects
*   `lifetime_hours` (number, optional): Chat lifetime in hours (default: 24)

**Headers:**
*   `X-API-KEY` (required)
*   `Content-Type: application/json`

##### Python Examples

##### Basic Usage Example

```python
import requests
import json

# Basic message example
def send_message():
    try:
        url = 'YOUR_AGENT_ZERO_URL/api_message'
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': 'YOUR_API_KEY'
        }
        payload = {
            'message': "Hello, how can you help me?",
            'lifetime_hours': 24
        }

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if response.ok:
            print('✅ Success!')
            print('Response:', data.get('response'))
            print('Context ID:', data.get('context_id'))
            return data
        else:
            print('❌ Error:', data.get('error'))
            return None
    except Exception as error:
        print('❌ Request failed:', error)
        return None

# Call the function
if __name__ == "__main__":
    result = send_message()
    if result:
        print('Message sent successfully!')
```

##### Conversation Continuation Example

```python
# Continue conversation example
def continue_conversation(context_id):
    try:
        url = 'YOUR_AGENT_ZERO_URL/api_message'
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': 'YOUR_API_KEY'
        }
        payload = {
            'context_id': context_id,
            'message': "Can you tell me more about that?",
            'lifetime_hours': 24
        }

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if response.ok:
            print('✅ Continuation Success!')
            print('Response:', data.get('response'))
            return data
        else:
            print('❌ Error:', data.get('error'))
            return None
    except Exception as error:
        print('❌ Request failed:', error)
        return None

# Example: First send a message, then continue the conversation
def full_conversation_example():
    first_result = send_message()
    if first_result and first_result.get('context_id'):
        continue_conversation(first_result['context_id'])

if __name__ == "__main__":
    full_conversation_example()
```

##### File Attachment Example

```python
import base64

# File attachment example
def send_with_attachment():
    try:
        # Example with text content (convert to base64)
        text_content = "Hello World from attachment!"
        base64_content = base64.b64encode(text_content.encode('utf-8')).decode('utf-8')

        url = 'YOUR_AGENT_ZERO_URL/api_message'
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': 'YOUR_API_KEY'
        }
        payload = {
            'message': "Please analyze this file:",
            'attachments': [
                {
                    'filename': "document.txt",
                    'base64': base64_content
                }
            ],
            'lifetime_hours': 12
        }

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if response.ok:
            print('✅ File sent successfully!')
            print('Response:', data.get('response'))
            return data
        else:
            print('❌ Error:', data.get('error'))
            return None
    except Exception as error:
        print('❌ Request failed:', error)
        return None

# Call the function
if __name__ == "__main__":
    send_with_attachment()
```

---

#### `GET/POST /api_log_get`

Retrieve log data by context ID, limited to a specified number of entries from the newest.

##### API Reference

**Parameters:**
*   `context_id` (string, required): Context ID to get logs from
*   `length` (integer, optional): Number of log items to return from newest (default: 100)

**Headers:**
*   `X-API-KEY` (required)
*   `Content-Type: application/json` (for POST)

##### Python Examples

##### GET Request Example

```python
# Get logs using GET request
def get_logs_get(context_id, length=50):
    try:
        url = 'YOUR_AGENT_ZERO_URL/api_log_get'
        params = {
            'context_id': context_id,
            'length': length
        }
        headers = {
            'X-API-KEY': 'YOUR_API_KEY'
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if response.ok:
            print('✅ Logs retrieved successfully!')
            print('Total items:', data['log'].get('total_items'))
            print('Returned items:', data['log'].get('returned_items'))
            print('Log items:', data['log'].get('items'))
            return data
        else:
            print('❌ Error:', data.get('error'))
            return None
    except Exception as error:
        print('❌ Request failed:', error)
        return None

# Example usage
if __name__ == "__main__":
    get_logs_get('ctx_abc123', 20)
```

##### POST Request Example

```python
# Get logs using POST request
def get_logs_post(context_id, length=50):
    try:
        url = 'YOUR_AGENT_ZERO_URL/api_log_get'
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': 'YOUR_API_KEY'
        }
        payload = {
            'context_id': context_id,
            'length': length
        }

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if response.ok:
            print('✅ Logs retrieved successfully!')
            print('Context ID:', data.get('context_id'))
            print('Log GUID:', data['log'].get('guid'))
            print('Total items:', data['log'].get('total_items'))
            print('Returned items:', data['log'].get('returned_items'))
            print('Start position:', data['log'].get('start_position'))
            print('Progress:', data['log'].get('progress'))
            print('Log items:', data['log'].get('items'))
            return data
        else:
            print('❌ Error:', data.get('error'))
            return None
    except Exception as error:
        print('❌ Request failed:', error)
        return None

# Example usage - get latest 10 log entries
if __name__ == "__main__":
    get_logs_post('ctx_abc123', 10)
```

---

#### `POST /api_terminate_chat`

Terminate and remove a chat context to free up resources. Similar to the MCP `finish_chat` function.

##### API Reference

**Parameters:**
*   `context_id` (string, required): Context ID of the chat to terminate

**Headers:**
*   `X-API-KEY` (required)
*   `Content-Type: application/json`

##### Python Examples

##### Basic Termination Examples

```python
# Basic terminate chat function
def terminate_chat(context_id):
    try:
        url = 'YOUR_AGENT_ZERO_URL/api_terminate_chat'
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': 'YOUR_API_KEY'
        }
        payload = {
            'context_id': context_id
        }

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if response.ok:
            print('✅ Chat deleted successfully!')
            print('Message:', data.get('message'))
            return data
        else:
            print('❌ Error:', data.get('error'))
            return None
    except Exception as error:
        print('❌ Request failed:', error)
        return None

# Example 1: Terminate a specific chat
if __name__ == "__main__":
    terminate_chat('ctx_abc123')

# Example 2: Complete workflow - send message, then terminate
def simple_workflow():
    # Send a message
    result = send_message()

    if result and result.get('context_id'):
        print('Chat created:', result['context_id'])

        # Do some work with the chat...
        # continue_conversation(result['context_id'])

        # Clean up when done
        terminate_chat(result['context_id'])
        print('Chat cleaned up')

# Run the workflow
if __name__ == "__main__":
    simple_workflow()
```

---

#### `POST /api_reset_chat`

Reset a chat context to clear conversation history while keeping the `context_id` alive for continued use.

##### API Reference

**Parameters:**
*   `context_id` (string, required): Context ID of the chat to reset

**Headers:**
*   `X-API-KEY` (required)
*   `Content-Type: application/json`

##### Python Examples

##### Basic Reset Examples

```python
# Basic reset chat function
def reset_chat(context_id):
    try:
        url = 'YOUR_AGENT_ZERO_URL/api_reset_chat'
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': 'YOUR_API_KEY'
        }
        payload = {
            'context_id': context_id
        }

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if response.ok:
            print('✅ Chat reset successfully!')
            print('Message:', data.get('message'))
            print('Context ID:', data.get('context_id'))
            return data
        else:
            print('❌ Error:', data.get('error'))
            return None
    except Exception as error:
        print('❌ Request failed:', error)
        return None

# Example 1: Reset a specific chat
if __name__ == "__main__":
    reset_chat('ctx_abc123')

# Example 2: Reset and continue conversation
def reset_and_continue():
    context_id = 'ctx_abc123'

    # Reset the chat to clear history
    reset_result = reset_chat(context_id)

    if reset_result:
        print('Chat reset, starting fresh conversation...')

        # Continue with same context_id but fresh history
        try:
            url = 'YOUR_AGENT_ZERO_URL/api_message'
            headers = {
                'Content-Type': 'application/json',
                'X-API-KEY': 'YOUR_API_KEY'
            }
            payload = {
                'context_id': context_id,  # Same context ID
                'message': "Hello, this is a fresh start!",
                'lifetime_hours': 24
            }

            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            print('New conversation started:', data.get('response'))
        except Exception as error:
            print('❌ Request failed:', error)

# Run the example
if __name__ == "__main__":
    reset_and_continue()
```

---

#### `POST /api_files_get`

Retrieve file contents by paths, returning files as base64 encoded data. Useful for retrieving uploaded attachments.

##### API Reference

**Parameters:**
*   `paths` (array, required): Array of file paths to retrieve (e.g., `["/a0/tmp/uploads/file.txt"]`)

**Headers:**
*   `X-API-KEY` (required)
*   `Content-Type: application/json`

##### Python Examples

##### File Retrieval Examples

```python
import base64

# Basic file retrieval
def get_files(file_paths):
    try:
        url = 'YOUR_AGENT_ZERO_URL/api_files_get'
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': 'YOUR_API_KEY'
        }
        payload = {
            'paths': file_paths
        }

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if response.ok:
            print('✅ Files retrieved successfully!')
            print('Retrieved files:', list(data.keys()))

            # Convert base64 back to text for display
            for filename, base64_content in data.items():
                try:
                    text_content = base64.b64decode(base64_content).decode('utf-8')
                    print(f"{filename}: {text_content[:100]}...")
                except Exception:
                    print(f"{filename}: Binary file ({len(base64_content)} chars)")

            return data
        else:
            print('❌ Error:', data.get('error'))
            return None
    except Exception as error:
        print('❌ Request failed:', error)
        return None

# Example 1: Get specific files
if __name__ == "__main__":
    file_paths = [
        "/a0/tmp/uploads/document.txt",
        "/a0/tmp/uploads/data.json"
    ]
    get_files(file_paths)

# Example 2: Complete attachment workflow
def attachment_workflow():
    # Step 1: Send message with attachments
    try:
        url = 'YOUR_AGENT_ZERO_URL/api_message'
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': 'YOUR_API_KEY'
        }
        
        text_content = "Hello, this is test content!"
        base64_content = base64.b64encode(text_content.encode('utf-8')).decode('utf-8')
        
        payload = {
            'message': "Please analyze this file",
            'attachments': [{
                'filename': "test.txt",
                'base64': base64_content
            }],
            'lifetime_hours': 1
        }

        message_response = requests.post(url, headers=headers, json=payload)

        if message_response.ok:
            print('Message sent with attachment')

            # Step 2: Retrieve the uploaded file
            retrieved_files = get_files(["/a0/tmp/uploads/test.txt"])

            if retrieved_files and "test.txt" in retrieved_files:
                original_content = base64.b64decode(retrieved_files["test.txt"]).decode('utf-8')
                print('Retrieved content:', original_content)
    except Exception as error:
        print('❌ Request failed:', error)

# Run the complete workflow
if __name__ == "__main__":
    attachment_workflow()
```
