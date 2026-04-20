
Be in the outer (pcp_to_cc_root) directory, then in terminal:

   source .venv/bin/activate

   uv pip install git+https://github.com/kramsman/gitupdater.git

or non-uv:

   or  pip install git+https://github.com/kramsman/gitupdater.git

You can put this in the docstring of scripts that need it
If you get an error "Gitupdater not found":
  1. go into terminal
  2. copy and enter: source .venv/bin/activate
  3. then enter: uv pip install git+https://github.com/kramsman/gitupdater.git
