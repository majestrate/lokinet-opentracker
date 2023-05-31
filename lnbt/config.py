class Config:
    pass


config = Config()

config.db_url = "sqlite:///:memory?check_same_thread=False"
config.interval = 60 * 5


# lokinet dns address
config.lokinet_dns = "127.3.2.1"
