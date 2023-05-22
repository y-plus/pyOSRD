![Logo](rlway.svg)

# OSRD

On WSL/Ubuntu

## Prerequisite

### Java17

```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt install openjdk-17-jdk openjdk-17-jre
```

### Poetry

```bash
pip install poetry
```

## Latest version

in your home directory

### First time

```bash
cd ~
git clone git@github.com:DGEXSolutions/osrd.git
```

### Update

```bash
cd ~/osrd/core
git pull
cd -
```

## Build core

```bash
cd ~/osrd/core
poetry --directory=../python/railjson_generator install
./gradlew processTestResources shadowJar
cd -
```

# Regulation

## OSRD PATH

Make sure the path to OSRD is indicated in the file `.env`

```
OSRD_PATH=/home/<your user name>/osrd
```

## Python

Make sure you have python3>=3.9 installed

## Virtual env

```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

##
