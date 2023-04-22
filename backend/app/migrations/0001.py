from app.configurator.documents import GameConfig


def run():
    # create initial game config
    GameConfig.apply_template()
