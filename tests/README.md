# Testing

You can run all tests with
```
python -m unittest discover -s tests --verbose
```

from the main directory. As you can see, there are two type of tests: [python](tests/python/) and [quantum](tests/quantum/).

Python tests make sure that the classical units of the program work properly.

Quantum tests, on the other hand, verify the quantum parts of the program. But since a quantum system is nondeterministic by nature, these tests are performed multiple times. The results are then averaged and compared with the expected result (with a specific margin of error).

By default, most quantum tests are run 500 times and evaluated with a margin of error of 7%. Tests that have only one expected outcome are run 100 times with a margin of error of 0%.

These quantum parameters can be modified in the module [init](tests/quantum/__init__.py) file. You can also choose to display the expected and obtained outcomes for each test.

Since each test is run many times, testing [quantum](tests/quantum/) takes about 10 minutes on an average computer (while [python](tests/python/) takes only 0.012 seconds). When you modify the parameters execution time will change, but so will the accuracy of the results. Some tests might fail if accuracy is reduced enough.

You can also just run only one of the modules
```
python -m unittest discover -s tests.python --verbose
python -m unittest discover -s tests.quantum --verbose

```

Or just a specific test

```
python -m unittest tests.python.test_name.TestClass.test
```
