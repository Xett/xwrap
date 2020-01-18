conda build .
conda install --use-local -y --force-reinstall $(git config --local remote.origin.url|sed -n 's#.*/\([^.]*\)\.git#\1#p')
conda build purge
