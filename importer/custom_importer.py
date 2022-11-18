import logging
from typing import Dict, List, Optional, Text, Union

import rasa.shared.data
from rasa.shared.core.training_data.structures import StoryGraph
from rasa.shared.importers import utils
from rasa.shared.importers import autoconfig
from rasa.shared.importers.importer import TrainingDataImporter
from rasa.shared.importers.autoconfig import TrainingType
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.core.domain import InvalidDomain, Domain
from rasa.shared.core.training_data.story_reader.yaml_story_reader import (
    YAMLStoryReader,
)
import rasa.shared.utils.io
from pymongo import MongoClient
import yaml
from collections import OrderedDict

logger = logging.getLogger(__name__)


class RasaFileImporter(TrainingDataImporter):
    """Default `TrainingFileImporter` implementation."""

    def __init__(
        self,
        config_file: Optional[Text] = None,
        domain_path: Optional[Text] = None,
        training_data_paths: Optional[Union[List[Text], Text]] = None,
        training_type: Optional[TrainingType] = TrainingType.BOTH,
    ):

        self._domain_path = domain_path

        self._nlu_files = rasa.shared.data.get_data_files(
            training_data_paths, rasa.shared.data.is_nlu_file
        )
        self._story_files = rasa.shared.data.get_data_files(
            training_data_paths, rasa.shared.data.is_story_file
        )
        self._conversation_test_files = rasa.shared.data.get_data_files(
            training_data_paths, rasa.shared.data.is_test_stories_file
        )

        self.config = autoconfig.get_configuration(config_file, training_type)

    async def get_config(self) -> Dict:
        """Retrieves model config (see parent class for full docstring)."""
        return self.config

    async def connect_db(self, database='default'):
        client = MongoClient('localhost:27017')
        db = client[database]
        try:
            serverStatusResult = db.command('serverStatus')
            pprint(serverStatusResult)
        except Exception as e:
            rasa.shared.utils.io.raise_warning(
                f"Connecting to MongoDB server error. Check the connection"
            )
        return client, db

    # overwrite db to stories.yml file.

    async def update_stories_files(self, db, collection):
        client, db = await self.connect_db(database=db)
        db_stories = {}
        stories_list = []
        for story in list(db[collection].find({}, {"_id": False})):
            stories_list.append(story.copy())
        db_stories['version'] = "2.0"
        db_stories['stories'] = stories_list
        with open('./data/stories.yml', 'w') as outfile:
            yaml.dump(db_stories, outfile, default_flow_style=False, allow_unicode=True, encoding="utf-8", sort_keys=False)
        print("Đã cập nhật xong file yml")
        return "OK"

    async def update_nlu_files(self, db, collection) -> None:
        client, db = await self.connect_db(database=db)
        class literal_unicode(str): pass

        def literal_unicode_representer(dumper, data):
            return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')

        yaml.add_representer(literal_unicode, literal_unicode_representer)

        db_nlu = {}
        nlu_list = []
        for nlu in list(db[collection].find({}, {"_id": False})):
            try:
                expanded_examples_nlu = nlu.copy()
                processed_dict = {'intent': expanded_examples_nlu.get('intent'),
                    'examples': literal_unicode(expanded_examples_nlu.get('examples'))}
                nlu_list.append(processed_dict)
            except Exception as e:
                print("error at {}".format(expanded_examples_nlu.get('intent')))
        db_nlu['version'] = "2.0"
        db_nlu['nlu'] = nlu_list
        with open('../data/nlu.yml', 'w') as outfile:
            yaml.dump(db_nlu, outfile, default_flow_style=False, default_style=None, allow_unicode=True, encoding="utf-8", sort_keys=False)
        print("Đã cập nhật xong file yml")
        return "OK"

    async def get_stories(
        self,
        template_variables: Optional[Dict] = None,
        use_e2e: bool = False,
        exclusion_percentage: Optional[int] = None,
    ) -> StoryGraph:
        """Retrieves training stories / rules (see parent class for full docstring)."""
        print("Các story files là: {}".format(self._story_files))
        updated_story_file = await self.update_stories_files(db="jewelry", collection="story")
        updated_nlu_file = await self.update_nlu_files(db="jewelry", collection="nlu")
        return await utils.story_graph_from_paths(
            self._story_files,
            await self.get_domain(),
            template_variables,
            use_e2e,
            exclusion_percentage,
        )

    async def get_conversation_tests(self) -> StoryGraph:
        """Retrieves conversation test stories (see parent class for full docstring)."""
        print(self._story_files)
        return await utils.story_graph_from_paths(
            self._conversation_test_files, await self.get_domain(), use_e2e=True,
        )

    async def get_nlu_data(self, language: Optional[Text] = "en") -> TrainingData:
        """Retrieves NLU training data (see parent class for full docstring)."""
        return utils.training_data_from_paths(self._nlu_files, language)

    async def get_domain(self) -> Domain:
        """Retrieves model domain (see parent class for full docstring)."""
        domain = Domain.empty()

        # If domain path is None, return an empty domain
        if not self._domain_path:
            return domain
        try:
            domain = Domain.load(self._domain_path)
        except InvalidDomain as e:
            rasa.shared.utils.io.raise_warning(
                f"Loading domain from '{self._domain_path}' failed. Using "
                f"empty domain. Error: '{e}'"
            )

        return domain
