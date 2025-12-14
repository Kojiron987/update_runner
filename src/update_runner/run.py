from update_runner.daemon import Daemon


def run() -> None:
    daemon = Daemon()
    daemon.run()


if __name__ == "__main__":
    run()
