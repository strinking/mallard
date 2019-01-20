#!/bin/bash
set -eu

if [[ $# -ne 1 ]]; then
	echo >&2 "Usage: $0 mallard-config.yaml"
	exit 1
fi

python_ver=python3.7
repo_dir="$(dirname "$0")"
dest_dir=~mallard/repo

if [[ -f "$repo_dir/misc/mallard.service" ]]; then
	service="$repo_dir/mallard.service"
else
	service="$repo_dir/misc/mallard.service"
fi

rm -rf "$dest_dir"
mkdir -p "$dest_dir"
cp -a "$repo_dir" "$dest_dir"
install -m400 "$1" "$dest_dir/config.yaml"
chown -R mallard:mallard "$dest_dir"
echo "Installed source code to '$dest_dir'"

"$python_ver" -m pip install -r "$repo_dir/requirements.txt"
echo "Installed Python dependencies"

install -m644 "$service" /usr/local/lib/systemd/system/mallard.service
chown root:root /usr/local/lib/systemd/system/mallard.service
echo "Installed systemd service"

systemctl daemon-reload
systemctl restart mallard.service
echo "Started mallard systemd service"
