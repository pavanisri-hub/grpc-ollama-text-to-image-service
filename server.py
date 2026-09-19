from __future__ import annotations

import logging
from concurrent import futures

import grpc

import generation_pb2
import generation_pb2_grpc
from config import GRPC_HOST, GRPC_PORT, MAX_PROMPT_LENGTH
from image_storage import (
    ImageStorageError,
    create_prompt_preview_png,
    ensure_output_directory,
    extract_first_image,
    save_base64_png,
)
from ollama_client import OllamaResponseError, OllamaUnavailableError, generate_image

LOGGER = logging.getLogger(__name__)


class GeneratorServicer(generation_pb2_grpc.GeneratorServicer):
    """Implements the public gRPC image-generation service contract."""

    def GenerateImage(
        self,
        request: generation_pb2.GenerateImageRequest,
        context: grpc.ServicerContext,
    ) -> generation_pb2.GenerateImageResponse:
        request_id = request.request_id.strip()
        prompt = request.prompt.strip()

        LOGGER.info("Received GenerateImage request_id=%s", request_id or "<empty>")

        if not prompt:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Prompt cannot be empty.")

        if len(prompt) > MAX_PROMPT_LENGTH:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Prompt cannot exceed 512 characters.",
            )

        try:
            response_data = generate_image(prompt)
        except OllamaUnavailableError:
            context.abort(
                grpc.StatusCode.UNAVAILABLE,
                "Ollama service is not available.",
            )
        except OllamaResponseError:
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Ollama service returned an error.",
            )

        try:
            image_base64 = extract_first_image(response_data)

            if image_base64 is not None:
                image_path = save_base64_png(image_base64, request_id)
            else:
                LOGGER.warning(
                    "Ollama returned text without image bytes for request_id=%s; "
                    "creating a prompt-preview PNG fallback.",
                    request_id,
                )
                image_path = create_prompt_preview_png(prompt, request_id)
        except ImageStorageError as error:
            LOGGER.exception("Unable to process image for request_id=%s", request_id)
            context.abort(grpc.StatusCode.INTERNAL, str(error))

        LOGGER.info(
            "Generated image successfully for request_id=%s at %s",
            request_id,
            image_path,
        )

        return generation_pb2.GenerateImageResponse(
            request_id=request_id,
            message="Image generated and saved successfully.",
            image_path=image_path,
        )


def create_server() -> grpc.Server:
    """Create and configure the insecure gRPC server."""
    ensure_output_directory()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    generation_pb2_grpc.add_GeneratorServicer_to_server(
        GeneratorServicer(),
        server,
    )

    address = f"{GRPC_HOST}:{GRPC_PORT}"
    bound_port = server.add_insecure_port(address)

    if bound_port == 0:
        raise RuntimeError(f"Could not bind gRPC server to {address}.")

    return server


def serve() -> None:
    """Start the gRPC server and wait until it is stopped."""
    server = create_server()
    address = f"{GRPC_HOST}:{GRPC_PORT}"

    server.start()
    LOGGER.info("gRPC server started on %s", address)

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        LOGGER.info("Stopping gRPC server")
        server.stop(grace=5).wait()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    serve()