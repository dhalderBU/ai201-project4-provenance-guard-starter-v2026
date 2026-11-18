"""Warm the isolated inference process without putting model loading in a request."""

def post_worker_init(worker):
    import inference_runtime
    inference_runtime.engine.start()


def worker_exit(server, worker):
    import inference_runtime
    inference_runtime.engine.close()
