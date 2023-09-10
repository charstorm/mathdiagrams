set -ex
src="mathdiagrams"
black $src
flake8 $src
mypy $src
