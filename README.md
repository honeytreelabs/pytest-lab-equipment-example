# Integrating Lab Equipment into pytest-Based Tests

This is a companion git repository to our article about [integrating lab equipment into pytest-based tests](https://honeytreelabs.com/posts/lab-equipment-py/).

## Usage Instructions

Clone this repository, then install the required dependencies:

``` shell
pip install -r requirements.txt
```

Ensure that this doesn't contaminate your environment. I use [pyenv](https://github.com/pyenv/pyenv) for this purpose.

To run the tests:

``` shell
pytest -v
```

Naturally, this will function correctly only when the mentioned lab equipment is connected to your machine.
