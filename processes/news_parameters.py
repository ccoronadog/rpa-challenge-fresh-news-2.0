from robocorp import workitems
from RPA.JSON import JSON
from RPA.Tables import Tables

class NewsParametersProducer:
    def __init__(self, config):
        """Load all global variables from config file"""
        self.json = JSON()
        self.table = Tables()
        self.config = config
        self.parameters_json_file = self.config.get("json_file")
        self.search_phrase = self.config.get("search_phrase")
        self.news_category = self.config.get("news_categoy")
        self.number_months = self.config.get("number_months")

    def produce_news_parameters(self):
        """Build work-items by params of news"""
        parameters_data = self._load_parameters_data_as_table()
        news_parameters = self._create_work_item_new_parameter(parameters_data)
        self._save_work_item_news_parameters(news_parameters)

    def _load_parameters_data_as_table(self):
        json_data = self.json.load_json_from_file(self.parameters_json_file)
        return self.table.create_table(json_data["value"])

    def _create_work_item_new_parameter(self, parameters_data):
        news_parameters = []
        for row in parameters_data:
            new_parameter = dict(
                search_phrase=row[self.search_phrase],
                news_category=row[self.news_category],
                number_months=row[self.number_months]
            )
            news_parameters.append(new_parameter)
        return news_parameters

    def _save_work_item_news_parameters(self, news_parameters):
        for new_parameter in news_parameters:
            variables = dict(parameters_data=new_parameter)
            workitems.outputs.create(variables)
