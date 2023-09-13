set -ex
src="mathdiagrams examples"
black $src
flake8 $src
mypy $src
