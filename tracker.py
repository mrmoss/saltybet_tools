#!/usr/bin/env python
import saltybet
import time

if __name__=='__main__':
	while True:
		try:
			salty=saltybet.client()
			while True:
				salty.run()
				time.sleep(0.1)
		except KeyboardInterrupt:
			exit(1)
		except Exception as error:
			print(error)
		exit(0)