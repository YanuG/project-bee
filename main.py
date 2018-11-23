import sys

from readSerial import ReadSerial

def main(args):
    readSerial = ReadSerial()
    readSerial.run()

if __name__ == "__main__":
    # run main 
    try:
      main(sys.argv)
    except KeyboardInterrupt:
      print ("end script")