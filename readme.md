lokinet bittorrent tracker


requires:

* python3-flask
* [python3-oxenc](https://github.com/oxen-io/oxen-encoding)
* python3-sqlalchemy
* python3-psycopg2
* python3-dnspython

running:

    FLASK_APP=lnbt.tracker FLASK_ENV=prod flask run -p 6680
