# Examples of AI agents

## Setup steps

### 1. Set up conda env

By default, we'll use Python3.12 (primarily since the packages are likely best supported with more recent Python versions).

```bash
conda create -n ai_agent_learning_examples python=3.12 -y
```

Then install the packages:

```bash
pip install -r requirements.txt
```

### 2. Activate direnv

Activate the direnv, which reads in `.envrc` and sets the PYTHONPATH appropriately.

```bash
direnv allow
```
