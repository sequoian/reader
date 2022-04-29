@echo off

cd ..
SET FLASK_APP=reader.py
SET FLASK_ENV=development
::"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" -incognito http://localhost:5000/
title Reddit Reader & workon rdb & flask run
