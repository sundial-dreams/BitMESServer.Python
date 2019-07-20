import sys
import os


def register_project():
    cur_path = os.path.abspath(os.path.dirname(__file__))
    root_path = os.path.split(cur_path)[0]
    dirs = os.listdir(root_path)
    sys.path.append(root_path)
    for d in dirs:
        sys.path.append(os.path.join(root_path, d))


# main
def main():
    from sanic import Sanic
    from api.routers import routers

    app = Sanic()
    cur_path = os.path.abspath(os.path.dirname(__file__))
    root_path = os.path.split(cur_path)[0]
    static_path = os.path.join(root_path, "static")

    def run_app(port: int):
        print(routers)
        for url, val in routers.items():
            app.add_route(uri = url, methods = val[0] if type(val[0]) == list else [val[0]], handler = val[1])
        app.static(file_or_directory = static_path, uri = "/static", stream_large_files = True)
        app.run(port = port)

    run_app(port = 8000)


if __name__ == "__main__":
    register_project()
    main()
