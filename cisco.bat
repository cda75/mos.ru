@echo off
F:
cd  F:\Info\Python\mos.ru
if "%1"=="" (
	C:\Python27\python F:\Info\Python\mos.ru\cisco.py
	) else (
	C:\Python27\python F:\Info\Python\mos.ru\cisco.py -action %1
	)
exit
