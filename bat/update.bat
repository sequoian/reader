@echo off
REM Update the database with posts from the last week

pushd ..
workon rdb & ^
populate.py all 200 week & ^
popd