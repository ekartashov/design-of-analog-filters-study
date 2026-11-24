#!/usr/bin/env bash
set -eu

# Discover host $HOME
HOST_HOME="$(distrobox-host-exec sh -lc 'printf %s "$HOME"')"

mkdir -p "$HOME" "$HOME/.config"

# Forward git config from host
if [ -f "/run/host${HOST_HOME}/.gitconfig" ]; then
  ln -sf "/run/host${HOST_HOME}/.gitconfig" "$HOME/.gitconfig"
fi
if [ -d "/run/host${HOST_HOME}/.config/git" ]; then
  rm -rf "$HOME/.config/git"
  ln -sf "/run/host${HOST_HOME}/.config/git" "$HOME/.config/git"
fi

