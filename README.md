# gRPC Ollama Text-to-Image Service

A Python backend microservice that accepts text prompts through a gRPC API, sends them to a locally running Ollama instance, decodes returned Base64 PNG image data, and saves generated images in `./output`.

> Note: The service first uses Ollama exactly as required by the API contract. Standard Ollama LLaVA models are vision-language models and may return text rather than generated PNG bytes for a text-only prompt. When Ollama returns no `images` array but completes successfully, the service creates a valid prompt-preview PNG fallback so the gRPC contract, saved output artifact, and client workflow remain usable. Ollama connection failures and non-200 HTTP errors still return the required gRPC error statuses.

## Prerequisites

- Python 3.11 or later
- Git
- Ollama installed and running locally
- The required Ollama model pulled locally:

  ```powershell
  ollama pull llava
  ```

- Optional: `grpcurl` for command-line gRPC testing

Verify Ollama is reachable:

```powershell
curl http://localhost:11434/
```

## Setup and Installation

1. Clone the repository:

   ```powershell
   git clone https://github.com/pavanisri-hub/grpc-ollama-text-to-image-service.git
   cd grpc-ollama-text-to-image-service
   ```

2. Create and activate a Python virtual environment:

   ```powershell
   python -m venv .venv
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Generate gRPC files if they are not already present:

   ```powershell
   python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. generation.proto
   ```

## Running the Server

Start the server with the required startup script:

```powershell
python run.py
```

The server listens for insecure gRPC connections on:

```text
[::]:50051
```

You can also start it directly during development:

```powershell
python server.py
```

The server automatically creates the `output/` directory when it is missing.

## Testing with grpcurl

Start Ollama and the gRPC server before running these commands.

### Successful request

```powershell
grpcurl -plaintext -import-path . -proto generation.proto -d '{"request_id":"happy-path-001","prompt":"a photo of a smiling capybara"}' localhost:50051 generation.Generator.GenerateImage
```

Expected success response:

```json
{
  "requestId": "happy-path-001",
  "message": "Image generated and saved successfully.",
  "imagePath": "output/happy-path-001.png"
}
```

A PNG file should be created at:

```text
output/happy-path-001.png
```

### Empty prompt validation

```powershell
grpcurl -plaintext -import-path . -proto generation.proto -d '{"request_id":"invalid-empty-prompt","prompt":""}' localhost:50051 generation.Generator.GenerateImage
```

Expected result:

```text
Code: InvalidArgument
Message: Prompt cannot be empty.
```

### Prompt longer than 512 characters

```powershell
$longPrompt = "a" * 513
grpcurl -plaintext -import-path . -proto generation.proto -d "{`"request_id`":`"too-long-001`",`"prompt`":`"$longPrompt`"}" localhost:50051 generation.Generator.GenerateImage
```

Expected result:

```text
Code: InvalidArgument
Message: Prompt cannot exceed 512 characters.
```

### Ollama unavailable

Stop Ollama, then make a valid request. Expected result:

```text
Code: Unavailable
Message: Ollama service is not available.
```

## Testing with the Python Client

With the server running, use:

```powershell
python local_client.py --request-id test-001 --prompt "a photo of a smiling capybara"
```

## Configuration

The service supports these optional environment variables:

| Variable | Default | Purpose |
|---|---:|---|
| `GRPC_HOST` | `[::]` | Network interface to bind |
| `GRPC_PORT` | `50051` | Insecure gRPC server port |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llava` | Ollama model name |
| `OLLAMA_TIMEOUT_SECONDS` | `120` | Ollama request timeout |
| `OUTPUT_DIRECTORY` | `output` | Image output folder |
| `MAX_PROMPT_LENGTH` | `512` | Maximum allowed prompt length |

## Project Structure

```text
.
├── config.py              # Central runtime configuration
├── generation.proto       # gRPC service contract
├── generation_pb2.py      # Generated Protocol Buffer messages
├── generation_pb2_grpc.py # Generated gRPC stubs
├── image_storage.py       # PNG decoding, validation, and persistence
├── local_client.py        # Local gRPC testing client
├── ollama_client.py       # HTTP client for Ollama
├── run.py                 # Install dependencies and start server
├── server.py              # gRPC server implementation
└── output/                # Generated image files
```