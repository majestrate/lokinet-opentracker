lokinet bittorrent tracker


requires:

* python3-flask
* [python3-oxenc](https://github.com/oxen-io/oxen-encoding)
* python3-sqlalchemy
* python3-psycopg2
* python3-dnspython

running:

    FLASK_APP=lnbt.tracker FLASK_ENV=prod flask run -p 6680

then set up to run behind nginx:

```
server {
  # you MUST change this listen directive to use your.lokinet.ip.here:80
  listen 127.0.0.1:80;
  location / {
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_pass http://127.0.0.1:6680;
  }
}
```
