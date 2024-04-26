#!/bin/bash

set -xe

# install chrome
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
google-chrome --version

# install chromedriver
cd /tmp/
# https://googlechromelabs.github.io/chrome-for-testing/#stable
wget -q https://storage.googleapis.com/chrome-for-testing-public/124.0.6367.91/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip
sudo mv chromedriver-linux64/chromedriver /usr/bin/chromedriver
chromedriver --version
