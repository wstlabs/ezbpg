from ezbpg import __version__

"""
Just a stub for now.
At present, we run the scripts under bin/ as our de-facto unit test.
"""

def test_version():
    assert __version__ == '0.1.3'

def main():
    test_version()

if __name__ == '__main__':
    main()

