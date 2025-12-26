# Run autoflake to remove unused imports and variables
autoflake --remove-all-unused-imports --in-place --recursive .

# Run isort to sort imports 
isort --profile black --line-length=120 -skip-gitignore --atomic --combine-as .

# Run Black to format code
black --line-length 120 .