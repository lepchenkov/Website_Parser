import json


def get_config_string():
    with open('config.json', 'r') as f:
        config = json.load(f)
    db_name = config['CONFIGURATION']['DB_NAME']
    db_type = config['CONFIGURATION']['DB_TYPE']
    admin_name = config['CONFIGURATION']['ADMIN_NAME']
    admin_password = config['CONFIGURATION']['ADMIN_PASSWORD']
    db_location = config['CONFIGURATION']['LOCATION']
    db_config = db_type + '://' + admin_name + ':' + admin_password \
                        + '@' + db_location + '/' + db_name
    return db_config
