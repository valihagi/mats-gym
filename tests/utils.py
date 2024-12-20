import time

from mats_gym.servers import DockerCarlaServer

def start_server(port: int, image: str, timeout: float = 5.0) -> DockerCarlaServer:
    server = DockerCarlaServer(
        image=image,
        world_port=port,
        headless=True,
        container_name=f"carla_server_{port}",
    )
    server.start()
    time.sleep(timeout)
    return server
