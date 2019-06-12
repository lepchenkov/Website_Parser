from celery import Celery
from downloader import Downloader
from db_configurator import get_config_string


app = Celery('periodic', broker='amqp://localhost//')
db_config = get_config_string()
download = Downloader(db_config, create_new_tables=False)

@app.task
def run_parsing_procedure():
    parse_products()

app.conf.beat_schedule = {
    "run_parsing_product_info": {
        "task": "periodic.parse_products",
        "schedule": 5.0
    }
}

def parse_products():
    download.parse_products_parameters(number_of_products_to_parse=10)
    return True
