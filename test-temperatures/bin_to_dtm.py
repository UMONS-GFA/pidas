import glob




def parseBinToDtm(bin_filename, dtm_filename):
    with open(dtm_filename, 'w', encoding='utf-8') as f:
        f.write("# DATE: " + str(time.strftime("%Y-%m-%d", time.gmtime())) + "\n")
        f.write("# PROG: " + sys.argv[0] + "\n")
        f.write("# SITE: " + "\n")
        f.write("# UDAS: " + "\n")
        f.write("# TITL: " + "\n")
        f.write("# CHAN: " + "YYYY MM DD HH NN SS 0001_() 0002_() 0003_() 0004_()" + "\n")


if __name__ == '__main__':
    parseBinToDtm('/home/christophe/pycharm/pidas/data-examples/correct.bin', 'ouput.dtm')