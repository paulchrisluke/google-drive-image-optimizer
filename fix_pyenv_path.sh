#!/bin/bash
# Fix pyenv PATH so shims are first, ensuring correct Python version
export PATH="$HOME/.pyenv/shims:$PATH"
# Ensure pyenv uses the local version
eval "$(pyenv init -)"
echo "pyenv shims are now first in PATH. Python version: $(python --version)" 