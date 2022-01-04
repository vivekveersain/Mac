from gensim.summarization.summarizer import summarize
from pandas.io.clipboard import clipboard_get, clipboard_set
import argparse

parser = argparse.ArgumentParser(description='Taking word count as argument')
parser.add_argument('word_count', type=int, nargs='?',  help='Summery Length')
args = parser.parse_args()
word_count = args.word_count
if word_count is None: word_count = 50

print(summarize(clipboard_get(), word_count = word_count))
