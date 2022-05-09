# The command line arguments are as follows:
# [1] = max_urls (an integer specifying how many pages to scrape)
# [2] = max_threads (an integer specifying max number of threads to use for the ThreadPoolExecutor)
# [3] = url_count_threshold (an integer specifying an amount of minimum unique links crawled in order for the whole site to be crawled 
# [4] = seed links in a .txt file separated by newline| Leave empty to use the default

maxurls=$1
maxthreads=$2
urlthresh=$3
seedfilepath=$4


python3 "./general-threaded-crawler.py" $maxurls $maxthreads $urlthresh $seedfilepath