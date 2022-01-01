class Config:
    pass


config = Config()

config.db_url = "postgresql://jeff:jeff@localhost/torrents"
config.interval = 60 * 5
