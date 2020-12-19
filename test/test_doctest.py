import doctest

import k3down2


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3down2))
    return tests
