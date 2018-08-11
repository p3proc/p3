class MockDevice:
    """A mock device to temporarily suppress output to stdout
    Similar to UNIX /dev/null.
    """
    def write(self, s):
        pass
