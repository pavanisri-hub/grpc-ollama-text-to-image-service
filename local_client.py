from __future__ import annotations

import argparse

import grpc

import generation_pb2
import generation_pb2_grpc


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Send a GenerateImage request to the local gRPC service."
    )
    parser.add_argument("--request-id", required=True, help="Unique request identifier")

    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="Text prompt for image generation")
    prompt_group.add_argument(
        "--empty-prompt",
        action="store_true",
        help="Send an intentionally empty prompt for validation testing",
    )

    parser.add_argument("--host", default="localhost", help="gRPC host")
    parser.add_argument("--port", default=50051, type=int, help="gRPC port")
    args = parser.parse_args()

    prompt = "" if args.empty_prompt else args.prompt
    target = f"{args.host}:{args.port}"

    try:
        with grpc.insecure_channel(target) as channel:
            stub = generation_pb2_grpc.GeneratorStub(channel)
            response = stub.GenerateImage(
                generation_pb2.GenerateImageRequest(
                    request_id=args.request_id,
                    prompt=prompt,
                ),
                timeout=180,
            )
    except grpc.RpcError as error:
        print(f"gRPC code: {error.code().name}")
        print(f"gRPC details: {error.details()}")
        raise SystemExit(1) from error

    print(f"request_id: {response.request_id}")
    print(f"message: {response.message}")
    print(f"image_path: {response.image_path}")


if __name__ == "__main__":
    main()