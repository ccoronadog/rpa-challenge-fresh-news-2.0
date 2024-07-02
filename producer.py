from robocorp.tasks import task
"""Import classes"""
from processes.config_manager import ConfigManager
from processes.news_parameters import NewsParametersProducer

# Init the configuration dictionary
config = ConfigManager("input/Config.xlsx")

# Create instance
news_parameters_producer = NewsParametersProducer(config)

#Execute task to produce work items by news parameters
@task
def produce_news_parameters_task():
    news_parameters_producer.produce_news_parameters()