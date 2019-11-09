# OMA.by catalog parser
Parser created for scraping data from building store catalog. Built with python, BS4 and requests. PostgreSQL database is used for data storage. The repository also contains API for data access. 

## Installation
To use this parser you have to clone the repository, install requirements.txt, create a postgreSQL database and fill in the json.config file. 

## Usage
After the installation you can execute oma.py file. This will initialize the first stage of parsing procedure that will take several hours. All necessary tables will be created automatically. After the first stage is complete (check logs) you can run the second stage parsing using oma_celery.py file which uses message broker and a worker.

## License
[ecl-2.0]https://opensource.org/licenses/ECL-2.0
