#!/usr/bin/env python
import sys

from readSerial import ReadSerial

def main(args):
    readSerial = ReadSerial()
    readSerial.run()

if __name__ == "__main__":
    # run main when this file is ran directly as an executable (is not imported from another script)
    try:
      main(sys.argv)
    except KeyboardInterrupt:
      print ("end script")