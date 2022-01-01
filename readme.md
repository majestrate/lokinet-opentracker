lokinet bittorrent tracker


requires:

* python3-flask
* python3-oxenc
* python3-sqlalchemy
* python3-psycopg2

running:

    FLASK_APP=lnbt.tracker FLASK_ENV=prod flask run -h localhost.loki -p 6680
