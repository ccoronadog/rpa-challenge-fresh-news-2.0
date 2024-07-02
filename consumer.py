from robocorp.tasks import task
from processes.config_manager import ConfigManager
from processes.process_news import ProcessNews

# Init the configuration dictionary
config = ConfigManager("input/Config.xlsx")

process_news = ProcessNews(config)

@task
def process_news_task():
    """Execute task to consume work items created by params"""
    process_news.consume_news_parameters()