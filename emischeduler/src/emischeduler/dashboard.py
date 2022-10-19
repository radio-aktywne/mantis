from multiprocessing import Process
from typing import Optional

from gevent.pywsgi import WSGIServer
from rqmonitor import monitor_blueprint
from rqmonitor.cli import create_app_with_blueprint
from rqmonitor.defaults import RQ_MONITOR_REFRESH_INTERVAL

from emischeduler.config.models import Config
from emischeduler.redis import make_url


class Dashboard:
    def __init__(self, config: Config) -> None:
        redis_url = make_url(
            config.db.host,
            config.db.port,
            password=config.db.password,
        )
        self.server = self.create_server(
            config.admin.host,
            config.admin.port,
            config.admin.username,
            config.admin.password,
            redis_url,
        )
        self.process: Optional[Process] = None

    @staticmethod
    def create_server(
        host: str, port: int, username: str, password: str, redis_url: str
    ) -> WSGIServer:
        app = create_app_with_blueprint(
            None, username, password, "", monitor_blueprint
        )
        app.config["RQ_MONITOR_REDIS_URL"] = redis_url
        app.config["RQ_MONITOR_REFRESH_INTERVAL"] = RQ_MONITOR_REFRESH_INTERVAL
        return WSGIServer((host, port), app, log=None)

    def start(self) -> None:
        def run(server: WSGIServer) -> None:
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                server.stop()

        if self.process is not None:
            raise RuntimeError("Already started.")
        self.process = Process(target=run, args=(self.server,))
        self.process.start()

    def end(self) -> None:
        if self.process is None:
            return
        self.process.kill()

    def kill(self) -> None:
        if self.process is None:
            return
        self.process.terminate()

    def wait(self) -> None:
        if self.process is None:
            return
        self.process.join()
