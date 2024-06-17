from robocorp.tasks import task
from robocorp import workitems
from RPA.JSON import JSON
from RPA.Tables import Tables


json = JSON()
table = Tables()

PARAMETERS_JSON_FILE = "output/news_parameters.json"

SEARCH_PHRASE = "SearchPhrase"
NEWS_CATEGORY = "NewsCategory"
NUMBER_MONTHS = "NumberMonths"

@task
def produce_news_parameters():
    """Construye los parámetros de las noticias por medio de work-items"""
    parameters_data = load_parameters_data_as_table()
    news_parameters = create_work_item_new_parameter(parameters_data)
    save_work_item_news_parameters(news_parameters)

def load_parameters_data_as_table():
    json_data = json.load_json_from_file(PARAMETERS_JSON_FILE)
    return table.create_table(json_data["value"])

def create_work_item_new_parameter(parameters_data):
    news_parameters = []
    for row in parameters_data:
        new_parameter = dict(
            search_phrase = row[SEARCH_PHRASE],
            news_category = row[NEWS_CATEGORY],
            number_months = row[NUMBER_MONTHS]
        )
        news_parameters.append(new_parameter)
    return news_parameters

def save_work_item_news_parameters(news_parameters):
    for new_parameter in news_parameters:
        variables = dict(parameters_data = new_parameter)
        workitems.outputs.create(variables)