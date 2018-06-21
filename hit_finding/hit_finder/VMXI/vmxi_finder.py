import reflections as ref
import argparse


def argparser(argv=None):
    parser = argparse.ArgumentParser(description = 'Hit Finder\n\
	                                 Analyses spot count data to produce an estimate\
	                                 of the hit rate for a given directory.\n\
	                                 EXAMPLE\n ./hit_finder.py')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument("-i" ,"--input_file", type=str, required=True)
    args = parser.parse_args()
    return args

def main(args):
   strong_pickle=args.input_file
   directory='.'
   all_strong=ref.get_num_reflections(strong,directory)
   print all_strong

if __name__ == '__main__':
   args=argparser()
   main(args)

