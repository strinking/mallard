#!/bin/bash
set -eu

if [[ $# -ne 1 ]]; then
	echo >&2 "Usage: $0 mallard-config.yaml"
	exit 1
fi

repo_dir="$(dirname "$0")"
dest_dir=~mallard/repo

rm -rf "$dest_dir"
mkdir -p "$dest_dir"
cp -a "$repo_dir" "$dest_dir"
install -m400 "$1" "$dest_dir/config.yaml"
chown -R mallard:mallard "$dest_dir"
echo "Installed source code to '$dest_dir'"

python3.6 -m pip install -r "$repo_dir/requirements.txt"
echo "Installed Python dependencies"

install -m644 "$repo_dir/misc/mallard.service" /usr/local/lib/systemd/system/mallard.service
chown root:root /etc/systemd/system/mallard.service
echo "Installed systemd service"

systemctl daemon-reload
systemctl restart mallard.service
echo "Started mallard systemd service"

