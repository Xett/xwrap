# Read Input Variables
setupName=$(git config --local remote.origin.url|sed -n 's#.*/\([^.]*\)\.git#\1#p')
setupVersion="0.1"
setupAuthor=$(git config user.name)
setupEmail=$(git config user.email)
setupUrl=$(git remote get-url origin)
setupDescription=$(python get-project-short-description.py $setupUrl)

# Set Directory Variables
dir=$(PWD) > /dev/null 2>&1
bin_dir=$dir"/bin"
package_dir=$dir"/"$setupName
old_name_project=`find * -type d -not -name "bin"`

# Remove bin folder if it already exists
[ -d $bin_dir ] && rm -R $bin_dir

# Check for missing directories
[ ! -d $bin_dir ] && mkdir $bin_dir
[ ! -d "$dir/anaconda_build" ] && mkdir "$dir/anaconda_build"
[ ! -d "$dir/anaconda_build/$setupName" ] && mkdir "$dir/anaconda_build/$setupName" && mv "$dir/bld.bat" "$dir/anaconda_build/$setupName/bld.bat" && mv "$dir/build.sh" "$dir/anaconda_build/$setupName/build.sh"

# Move old package to new package folder
[[ $old_name_project ]] && mv -v $dir"/"$old_name_project $package_dir
[ ! -d $package_dir ] && mkdir $package_dir

# Create setup.py
printf "import setuptools\nwith open(\"README.md\",\"r\") as fh:\n\tlong_description=fh.read()\nsetuptools.setup(\n\tname=\'$setupName\',\n\tversion=\'$setupVersion\',\n\tscripts=[\'bin/$setupName\'],\n\tauthor=\'$setupAuthor\',\n\tauthor_email=\'$setupEmail\',\n\tdescription=\'$setupDescription\',\n\tlong_description=long_description,\n\tlong_description_content_type=\"text/markdown\",\n\turl=\'$setupUrl\',\n\tpackages=setuptools.find_packages(),\n\tclassifiers=[\n\t\t\"Programming Language :: Python :: 3\",\n\t\t\"License :: OSI Approved :: MIT License\",\n\t\t\"Operating System :: OS Independent\",\n\t]\n)" > setup.py

# Create bin script
printf "#!/usr/bin/env python\nimport $setupName" > $bin_dir"/"$setupName

# Create Anaconda meta.yaml
printf "package:\n  name: $setupName\n  version: $setupVersion\n\nsource:\n  path: ./$setupName\n\nrequirements:\n  build:\n    - python\n    - setuptools\n\n  run:\n    - python\n\nabout:\n  home: $setupUrl" >  "$dir/anaconda_build/$setupName/meta.yaml"

# Clean the directory of this project
rm $dir"/setup-project.sh"
rm $dir"/get-project-short-description.py"
printf "" > .gitignore
