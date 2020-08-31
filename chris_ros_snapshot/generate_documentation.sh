#!/bin/bash

OUTPUT_DIRECTORY="docs/html"
mkdir -p $OUTPUT_DIRECTORY
python_files=$(ls *.py)
for python_file in $python_files; do
    module_name=$(echo $python_file | sed 's/.py//g')
    echo "Generating documentation for module $module_name..."
    pydoc -w $module_name
    mv $module_name.html $OUTPUT_DIRECTORY
done
echo "Done. See $OUTPUT_DIRECTORY for documentation."
