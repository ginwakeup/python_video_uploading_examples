import grpc
import os
import cv2
import numpy as np
import base64

from concurrent import futures

from gunner.grpc_stream.grpc_video import service_pb2_grpc, response_pb2


class VideoUploadServer(service_pb2_grpc.VideoUploadServicer):
    def __init__(self):
        if not os.path.exists("output"):
            os.makedirs("output", exist_ok=True)

        self._count = 0

    def _frame_to_file(self, frame: bytes):
        b64e = base64.b64decode(frame)

        image = np.asarray(bytearray(b64e), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_UNCHANGED)

        cv2.imwrite(f"output/output_{self._count}.jpg", image)
        self._count += 1

    def Upload(self, request_iterator, context):
        for request in request_iterator:
            self._frame_to_file(request.data)

        response = response_pb2.UploadStatus(message="", code=response_pb2.OK)
        return response

    def UploadBi(self, request_iterator, context):
        for request in request_iterator:
            self._frame_to_file(request.data)
            yield response_pb2.UploadStatus(message="", code=response_pb2.OK)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_VideoUploadServicer_to_server(VideoUploadServer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()

    while True:
        pass


if __name__ == '__main__':
    serve()
