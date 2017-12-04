
## How To Run  

1. Clone source codes to local directory on above "TEST RUN" machine
```bash
git clone git@10.8.176.174:dguo/vdsm-auto.git
```
2. Install the dependency packages
```bash
pip install -r requirements
```
3. Config the variable in the "tests/v41/conf.py" file
4. Run the test cases by pytest
```bash
pytest -s -v tests/v41/test_nfs.py tests/v41/test_local.py ...
```
