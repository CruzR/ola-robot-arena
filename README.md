# OpenLab Robot Arena #

This repository contains the code for the robot arena hackathon we ran
December 1st and 2nd 2018.

## Installation ##

OS Dependencies:

 - [xwiimote](https://github.com/dvdhrm/xwiimote) \[[AUR](https://aur.archlinux.org/packages/xwiimote-git/)\]
 - [Python bindings for xwiimote](https://github.com/dvdhrm/xwiimote-bindings) \[[AUR](https://aur.archlinux.org/packages/python-xwiimote-git/)\]

Create a virtual environment:

```
python -m venv --system-site-packages env
```

Activate virtual environment:

```
source env/bin/activate
```

Install additional dependencies from pip:

```
python -m pip install sanic matplotlib
```

Generate SSL certificate:

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
```

Start xwiimote-server:

```
python robot_control.py
```

Start web API:

```
python webapi.py
```
