git clone git@github.com:bunsamosa/bowled_server_setup.git
rsync -av --exclude '.git' bowled_server_setup/ ./
rm -rf bowled_server_setup
