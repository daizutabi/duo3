import os

ROOT = os.path.join(os.path.expanduser('~'), '.duo3')

if not os.path.exists(ROOT):
    os.makedirs(ROOT)
