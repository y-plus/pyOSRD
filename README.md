![Logo](pyosrd.png)

Python API for Open Source Railway Designer https://osrd.fr/en/

# Prerequisites

## Python >= 3.10

## SSH keys to access github.com

https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account


## Java 17

### Install on Ubuntu

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install openjdk-17-jdk openjdk-17-jre
```
### Install on Windows

https://www.oracle.com/java/technologies/downloads/#java17

# For users

## Installation

```bash
pip install git+ssh://git@github.com/y-plus/pyOSRD.git@main
```
or
```bash
pip install --upgrade git+ssh://git@github.com/y-plus/pyOSRD.git@main
```

## Getting started

```python3
>>> from pyosrd import OSRD
>>> sim = OSRD(use_case='point_switch', dir='point_switch')
```

## Custom Java binary path

Create a file name `.env` at the root of your projet, containing
```bash
JAVA="<Your custon Java Path>"
```
On Windows, it is recommanded to use triple double quotes (especially if the path contains spaces), e.g.:
```bash
JAVA="""C:\Program Files\Common Files\Oracle\Java\javapath\java"""
```
# For contributors

```bash
git clone git@github.com:y-plus/pyOSRD.git
cd pyOSRD/
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```
