sudo apt-get update
sudo apt-get install -y bash-completion python3-venv
python3 -m venv .venv
. .venv/bin/activate
pip3 install mkdocs mkdocs-techdocs-core
