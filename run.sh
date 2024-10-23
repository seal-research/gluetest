#!/bin/sh

echo "Running tests for commons-cli and commons-cli-graal..."

mvn -f commons-cli/pom.xml test -Drat.skip || echo "Tests for the original commons-cli failed! Please ensure your environment is set up correctly and try again."
original_tests=$?

mvn -f commons-cli-graal/pom.xml test -Drat.skip || echo "Tests for the GraalVM version of commons-cli failed! Please ensure your environment is set up correctly and try again."
glue_code_tests=$?

mvn -f commons-csv/pom.xml test -Drat.skip || echo "Tests for commons-csv failed! Please ensure your environment is set up correctly and try again."
csv_tests=$?

mvn -f commons-csv-graal/pom.xml test -Drat.skip || echo "Tests for the GraalVM version of commons-csv failed! Please ensure your environment is set up correctly and try again."
csv_graal_tests=$?

# check python version greater than 3.10, print version if true
python3 -c 'import sys; \
            assert sys.version_info >= (3, 10), "Python version must be greater than 3.10!"; \
            print(f"Python version installed: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")'
python_installed=$?

# check pytest is installed 
python3 -c "import pytest; \
            print(f'Pytest version installed: {pytest.__version__}')"
pytest_installed=$?

if [ $python_installed -eq 0 ] && [ $pytest_installed -eq 0 ]; then
    echo "Running tests for commons-cli-python..." 
    python3 -m pytest commons-cli-python

    echo "Running tests for commons-csv-python..."
    python3 -m pytest commons-csv-python
fi

# print success message if all tests passed
if [ $original_tests -eq 0 ] && [ $glue_code_tests -eq 0 ] && [ $python_installed -eq 0 ] && [ $pytest_installed -eq 0 ] && [ $csv_tests -eq 0 ] && [ $csv_graal_tests -eq 0 ]; then
    echo "All tests passed!"
fi
