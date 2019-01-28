"""
This program generates a report from kernel areas that are triggered
by an application. It prints out the lines of each source file that are
used according the coverage info from gcov-kernel.

Author: Ali Gholami

"""
import sys, os, string, getopt

def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print 'analyzer.py -i <coverage.info> -o <outputfile>'
      sys.exit(2)

   for opt, arg in opts:
      if opt == '-h':
         print 'analyzer.py -i <coverage.info> -o <outputfile>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg   

   if os.path.isfile(inputfile):
     infile = open(inputfile, 'r')
     outfile = open(outputfile, 'w')
     kernel_usage(infile, outfile)
     infile.close()
     outfile.close()
   else:
     print "File: ", inputfile, " does not exist!"
     sys.exit(2)

"""
This function generates the lines that are used used by each source file in the kernel.
"""

def kernel_usage(infile, outfile):
    
    """
    A set of lines used in the SF. Each SF might be run several times
    and therefore we need a way to make each run identical: 

    SF:/usr/src/linux-3.13.0/arch/x86/include/asm/atomic.h
    DA:38,3
    DA:117,3
    LF:2
    LH:2

    SF:/usr/src/linux-3.13.0/arch/x86/include/asm/atomic.h:                                                                                                              
    DA:38,3
    DA:40:0
    DA 117,30
    LF:2                                                                                                                                                                 
    LH:2   

    Result will be as follow which duplicated lines are removed:

    SF:/usr/src/linux-3.13.0/arch/x86/include/asm/atomic.h                                                                                                               
    DA:38                                                                                                                                                              
    DA:117
    """
    da_values = set()
    
    "Create a unique mapping of SFs with the executed lines-"
    usage_dict = {}    
    
    "Put the SF path in a tmp variable to test if it already exist not to be duplicated."
    tmp_path= ""

    "Generate the executed lines for each SF and write the unique results in an outputfile."
    for lines in infile:
      if ("SF:" in lines):
        tmp_path = lines.rstrip(os.linesep)
      
      if ("DA:" in lines) and ("FNDA" not in lines):
        lines = lines.replace("DA:", "")
        line = lines.split(",")
         
        if ("=====" not in line[1]):
          if(int(line[1]) > 0):
            da_values.add(int(line[0]))

      if ("end_of_record" in lines):
        tmp_set = usage_dict.get(tmp_path)
        if tmp_set is not None:
          union = set().union(da_values,tmp_set)
          usage_dict[tmp_path] = union.copy()
        else:
          usage_dict[tmp_path]= da_values.copy()
        da_values.clear()


    
    for sf,da in usage_dict.iteritems():
      if(da):
        outfile.write(sf+'\n')
        da_sorted = sorted(da)
        for lines in da_sorted:
          outfile.write('%d\n'%lines)
         
        outfile.write('\n')

    pass


if __name__ == "__main__":
   main(sys.argv[1:])
