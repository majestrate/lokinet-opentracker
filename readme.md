lokinet bittorrent tracker (broken rn)

requires:

* python3-flask
* [python3-oxenc](https://github.com/oxen-io/oxen-encoding)
* python3-redis
* python3-dnspython

running:

    FLASK_APP=lnbt.tracker FLASK_ENV=prod flask run -p 6680

then set up to run behind nginx:

```
server {
  listen put_local_lokinet_ip_here:80;
  server_name tracker.whatever.loki;
  location / {
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_pass http://127.0.0.1:6680;
  }
}
```
