# Artifact for GlueTest

This is an artifact for the paper, "GlueTest: Testing Code Translation via Language Interoperability" presented at ICSME 2024 NIER. It contains the following directories: 

1. `commons-cli` and `commons-csv`: original Commons CLI and CSV source code and tests
2. `commons-cli-python` and `commons-csv-python`: translated code and tests in python
3. `commons-cli-graal` and `commons-csv-graal`: python source code, java tests, and (Java) glue code for GraalVM
4. `graal-glue-generator`: contains the source code for the glue code generator
5. `scripts`: contains scripts run local coverage, coverage through CI, collecting clients, and generating glue code.

## Setting up GraalVM and GraalPython

To run the GraalVM integration, we need to install the GraalVM SDK and the python component. To install GraalVM, we use the SDKMAN! tool. To install SDKMAN!, run the following command [from the SDKMAN! website](https://sdkman.io/install):
```bash
curl -s "https://get.sdkman.io" | bash
```
After installing SDKMAN!, we can install GraalVM (Java 17) using the following command from their [website](https://www.graalvm.org/downloads/):
```bash
sdk install java 17.0.7-graal
```
After installing GraalVM, we need to install the python component. To do so, we run:
```bash
gu install python
```
## Running Tests
All commands for running tests can be found in the `run.sh` file in the root directory, and can be run with:
```bash
bash run.sh
```

To see a description for each command, please see the following sections.


### Running the original Java tests
```bash
# Commons CLI
mvn -f commons-cli/pom.xml test -Drat.skip
# Commons CSV
mvn -f commons-csv/pom.xml test -Drat.skip
```
> NOTE: This step requires maven to be installed. If maven is not installed, see [their web page](https://maven.apache.org/install.html) for installation instructions.

### Running the translated Python Tests

In order to run the python tests, `pytest` is needed and can be installed with the following command:
```bash
python -m pip install pytest
```
Then, the python tests can be run with:
```bash
# Commons CLI
pytest commons-cli-python
# Commons CSV
pytest commons-csv-python
```
> NOTE: We use CPython 3.11.4 for running our translation tests. Please ensure a compatible of Python is installed before running tests.

### Running glue code tests with GraalVM
```bash
# Commons CLI
mvn -f commons-cli-graal/pom.xml test -Drat.skip
# Commons CSV
mvn -f commons-csv-graal/pom.xml test -Drat.skip
```

## Measure coverage
Coverage for our glue code is measured using a python script, `cover.py` in the `scripts/` directory. To run coverage, we run the local version of our script:
```bash
python scripts/coverage/cover_local.py 
```

## Running the Glue Automation
To automatically generate glue for all classes in Commons CLI and Commons CSV, run the following from the root directory:
```bash
python scripts/generate_glue.py
```

The glue code automation will generate the files under the `generated/commons-cli` and `generated/commons-csv` directories, which can be used as drop-in replacements for the glue code in `commons-cli-graal` and `commons-csv-graal` respectively.

## Collecting Clients
We provide the scripts for scraping clients under `scripts/clients/selenium.py`. The `scripts/clients/bash_script_version.sh` script can further be used to extract the versions of the libraries used by the clients.
