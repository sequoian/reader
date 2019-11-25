@echo off

pushd ..
workon rdb & ^
populate.py %* & ^
popd