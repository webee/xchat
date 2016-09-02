x_forwarded_for_header="X-FORWARDED-FOR"


def on_starting(server):
    print("starting...")


def post_fork(server, worker):
    print("post fork")
