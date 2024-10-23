## Measurement of Python code coverage by Java tests through Graal

1. CI script runs coverage measurement automatically after commits/pull requests to `main`.
2. `common_local.py` can be used to run the coverage measurement locally. Make sure you have GraalVM (and Graalpy) and other Java dependencies installed. 

> **Warning**
> This script is destructive when run locally. Please make sure that you stage all changes in the repository before running this, and discard any new changes after the script terminates and you record the coverage.
