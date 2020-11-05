### Overview

MedSpider is a collection of scripts that help with web scraping tasks in order to gather online conversations from health forums. MedSpider targets the following listed online forums, which are categorized by the type of interaction between **Patients (P)** and **Medics (M)**.

### General Requirements

- [Python 2.7](https://www.python.org/downloads)
- Latest version of [lxml](http://lxml.de) installed via `pip install lxml==4.1.0`
- [Pandas](https://pypi.org/project/pandas/) is also needed for some of the scrapers

### [BMJ's Doc2Doc Discussions](https://web.archive.org/web/20160615105956/http://doc2doc.bmj.com/) [M2M]

1. Please note that the BMJ's Doc2Doc forum is discontinued, the scraper uses cached web pages from [Wayback Machine/Internet Archive](https://archive.org)
2. Specify the output directory to write results to by editing the `doc2doc.py` file's main entry point, e.g. `Spidey().crawl('doc2doc')` (default is `doc2doc` if not specified)
3. Run the script via command line or terminal `python doc2doc.py` which will create tab-separated output files in the output directory you specified

### [DocCheck Blogs](http://www.doccheck.com/com/ask/) [M2M]

1. This scraper will require [registration](http://www.doccheck.com/com/account/register/) of a medic-related account on DocCheck
2. Specify the output directory to write results to by editing the `doccheck.py` file's main entry point, e.g. `Spidey().crawl('doccheck')` (default is `doccheck` if not specified)
3. Run the script via command line or terminal `python doccheck.py` which will create tab-separated output files in the specified directory: `blogs.tsv`, `comments.tsv`, and `topics.tsv`

### [eHealth Forum Questions](https://ehealthforum.com/health/ask_a_doctor_forums.html) [P2M]

1. Specify the output directory to write results to by editing the `ehealthforum.py` file's main entry point, e.g. `Spidey().crawl('ehealthforum')`  (default is `ehealthforum` if not specified)
2. Run the script via command line or terminal `python ehealthforum.py` which will create a tab-separated output file called `chats.tsv` in the specified directory
3. To run the unit tests, use `pytest -q ehealthforum.py`

### Scrape the [Doctors Lounge Forum](https://www.doctorslounge.com/forums/) in 3 Steps [P2M]

1. Specify the output directory to write results to by editing the `doctorslounge.py` file's main entry point, e.g. `Spidey().crawl('doctorslounge')`   (default is `doctorslounge` if not specified)
2. Run the script via command line or terminal `python doctorslounge.py` which will create a tab-separated output file called `discussions.tsv` in the specified directory
3. To run the unit tests, use `pytest -q doctorslounge.py`

### Scrape the [Optimal Health Network (OHN) Live Chat Archives](https://web.archive.org/web/20130129082319/http://www.optimalhealthnetwork.com/Alternative-Health-Live-Chat-Log-Archive-s/196.htm) in 3 Steps [P2M]

1. Specify the output directory to write results to by editing the `ohn.py` file's main entry point, e.g. `Spidey().crawl('ohn')` (default is `ohn` if not specified)
2. Run the script via command line or terminal `python ohn.py` which will create a tab-separated output file called `chats.tsv` in the specified directory
3. To run the unit tests, use `pytest -q ohn.py`

### [Johns Hopkins Breast Center Expert Answers](http://www.hopkinsbreastcenter.org/services/ask_expert/) in 3 Steps [P2M]

1. Specify the output file to write results to by editing the `hopkins.py` file's main entry point, e.g. `Spidey().crawl('hopkins')` (default is 'hopkins' if not specified)
2. Run the script via command line or terminal `python hopkins.py` which will create a tab-separated output file called `discussions.tsv` in the specified directory
3. To run the unit tests, use `pytest -q hopkins.py`

### Scrape the [Health Stack Exchange Q&A Forums](https://health.stackexchange.com/questions?pagesize=50&sort=newest) in 3 Steps [P2P]

1. Specify the output directory (must exist) to write results to by editing the `healthse.py` file's main entry point, e.g. `Spidey().crawl('healthse')` (default is 'healthse' if not specified)
2. Run the script via command line or terminal `python healthse.py` which will create a collection of tab-separated output files (please note that Stack Exchange has rate limits): `questions.tsv`, `answers.tsv`, `question_comments.tsv`, and `answer_comments.tsv`.
3. To run the unit tests, use `pytest -q healthse.py`

### Parse the [Health Stack Exchange Q&A Archives](https://archive.org/download/stackexchange) in 3 Steps [P2P]

1. Download the [`health.stackexchange.com.7z`](https://archive.org/download/stackexchange) archive file and extract it using [7-Zip](http://www.7-zip.org/download.html), it has Ubuntu and Windows versions
2. Note the dataset folder where the extracted XML files are located
3. The `SEParser.py` script can create question pairs using the XML files via `python SEParse.py dataset-folder`, for example `python SEParse.py SEparse`. It will save the results to a CSV file within the dataset folder (in the case of the example, the file will be called `SEparse.csv`). The script can be modified to perform other extraction and parsing tasks from the XML files.