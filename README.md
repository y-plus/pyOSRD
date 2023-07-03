![Logo](rlway.svg)

# Prerequisites

- ssh keys to access github.com
- Python >= 3.9
- Java17

```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt install openjdk-17-jdk openjdk-17-jre
```

# For users

```bash
pip install git+ssh://git@github.com/y-plus/RLway.git
```

## Getting started

```python3
>>> from rlway.pyosrd import OSRD
>>> sim = OSRD(use_case='divergence', dir='divergence')
```

# For developers

```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

##
