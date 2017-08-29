sudo cp -r . /home/mallard/dev/mallard && sudo chown -R mallard /home/mallard/dev
sudo cp mallard.service /etc/systemd/system && sudo systemctl daemon-reload && sudo systemctl restart mallard
