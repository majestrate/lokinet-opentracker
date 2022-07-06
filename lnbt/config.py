class Config:
    pass


config = Config()

config.db_url = "postgresql://jeff:jeff@localhost/torrents"
config.interval = 60 * 5


# lokinet dns address
config.lokinet_dns = '127.3.2.1'
