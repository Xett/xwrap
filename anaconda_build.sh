setupName=$(git config --local remote.origin.url|sed -n 's#.*/\([^.]*\)\.git#\1#p')
conda build "./anaconda_build/$setupName"
conda install --use-local -y --force-reinstall $setupName 
conda build purge
