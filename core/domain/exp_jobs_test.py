# coding: utf-8
#
# Copyright 2014 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Jobs for explorations."""

__author__ = 'Frederik Creemers, Marcel Schmittfull'

"""Tests for ExpSummary continuous computations."""

import collections
import datetime

from core import jobs
from core import jobs_registry
from core.domain import config_services
from core.domain import event_services
from core.domain import exp_domain
from core.domain import exp_jobs
from core.domain import exp_services
from core.domain import rights_manager
from core.platform import models
(job_models, exp_models,) = models.Registry.import_models([
   models.NAMES.job, models.NAMES.exploration])
search_services = models.Registry.import_search_services()
from core.tests import test_utils

import feconf
import utils


class ModifiedExpSummaryAggregator(exp_jobs.ExpSummaryAggregator):
    """A modified ExpSummaryAggregator that does not start a new batch
    job when the previous one has finished.
    """
    @classmethod
    def _get_batch_job_manager_class(cls):
        return ModifiedExpSummaryMRJobManager

    @classmethod
    def _kickoff_batch_job_after_previous_one_ends(cls):
        pass


class ModifiedExpSummaryMRJobManager(exp_jobs.ExpSummaryMRJobManager):

    @classmethod
    def _get_continuous_computation_class(cls):
        return ModifiedExpSummaryAggregator


class ExpSummaryAggregatorUnitTests(test_utils.GenericTestBase):
    """Tests for ExpSummary aggregations."""

    ALL_CONTINUOUS_COMPUTATION_MANAGERS_FOR_TESTS = [
        ModifiedExpSummaryAggregator]

    def test_all_exps_publicized(self):
        """Test exploration summary batch job if all explorations are publicized."""

        # specify explorations that will be used in test
        exp_specs = [
            {'category': 'Category A',
             'title': 'Title 1'},
             {'category': 'Category B',
            'title': 'Title 2'},
            {'category': 'Category C',
             'title': 'Title 3'},
            {'category': 'Category A',
             'title': 'Title 4'},
            {'category': 'Category C',
             'title': 'Title 5'}
            ]

        self._run_batch_job_once(
            exp_specs,
            default_status=rights_manager.EXPLORATION_STATUS_PUBLICIZED)

    def test_all_exps_public(self):
        """Test gallery batch job if all explorations are public
        but not publicized."""

        exp_specs = [
            {'category': 'Category A',
             'title': 'Title 1'},
            {'category': 'Category B',
             'title': 'Title 2'},
            {'category': 'Category C',
             'title': 'Title 3'},
            {'category': 'Category A',
             'title': 'Title 4'},
            {'category': 'Category C',
             'title': 'Title 5'}]

        self._run_batch_job_once(
            exp_specs,
            default_status=rights_manager.EXPLORATION_STATUS_PUBLIC)

    def test_exps_some_publicized(self):
        """Test gallery batch job if some explorations are publicized."""

        exp_specs = [
            {'category': 'Category A',
             'status': rights_manager.EXPLORATION_STATUS_PUBLIC,
             'title': 'Title 1'},
            {'category': 'Category B',
             'status': rights_manager.EXPLORATION_STATUS_PUBLICIZED,
             'title': 'Title 2'},
            {'category': 'Category C',
             'status': rights_manager.EXPLORATION_STATUS_PRIVATE,
             'title': 'Title 3'},
            {'category': 'Category A',
             'status': rights_manager.EXPLORATION_STATUS_PUBLICIZED,
             'title': 'Title 4'},
            {'category': 'Category C',
             'status': rights_manager.EXPLORATION_STATUS_PUBLICIZED,
             'title': 'Title 5'}]

        self._run_batch_job_once(exp_specs)

    def _run_batch_job_once(
            self, exp_specs,
            default_title='A title',
            default_category='A category',
            default_status=rights_manager.EXPLORATION_STATUS_PUBLICIZED):
        """Test gallery batch job. exp_specs is a list of dicts with
        exploration specifications. Allowed keys are category, status, title.
        If a key is not specified, the default value is taken.
        """
        with self.swap(
                jobs_registry, 'ALL_CONTINUOUS_COMPUTATION_MANAGERS',
                self.ALL_CONTINUOUS_COMPUTATION_MANAGERS_FOR_TESTS):

            # default specs
            default_specs = {'title': default_title,
                             'category': default_category,
                             'status': default_status}

            self.register_editor('admin@example.com')
            self.login('admin@example.com')
            self.owner_id = self.get_user_id_from_email('admin@example.com')
            self.set_admins(['admin@example.com'])

            # get dummy explorations
            num_exps = len(exp_specs)
            expected_gallery_output = {}  # collections.defaultdict(list)
            from core.domain import exp_services
            for ind in range(num_exps):
                exp_id = str(ind)
                spec = default_specs
                spec.update(exp_specs[ind])

                self.save_new_valid_exploration(
                    exp_id,
                    self.owner_id,
                    title=spec['title'])
                exploration = exp_services.get_exploration_by_id(exp_id)
                exploration.category = spec['category']

                exp_services.save_new_exploration(self.owner_id, exploration)

                if spec['status'] == rights_manager.EXPLORATION_STATUS_PUBLICIZED:
                    # publicize exploration
                    rights_manager.publish_exploration(self.owner_id, exp_id)
                    rights_manager.publicize_exploration(self.owner_id, exp_id)

                # do not include user_id here, so all explorations are not
                # editable for now (will be updated depending on user_id
                # in galleries)
                is_editable = False
                exp_model = exp_models.ExplorationModel.get(exp_id)
                exp_rights_model = exp_models.ExplorationRightsModel.get(exp_id)
                summary_dict = {'id': exp_model.id,
                            'title': exp_model.title,
                            'category': exp_model.category,
                            'objective': exp_model.objective,
                            'language_code': exp_model.language_code,
                            'last_updated': utils.get_time_in_millisecs(exp_model.last_updated),
                            'status': exp_rights_model.status,
                            'community_owned': exp_rights_model.community_owned,
                            'is_editable': is_editable}

                exploration = exp_services.get_exploration_by_id(exp_id)
                # TODO(msl): manually create the summary model specifying title, category, etc
                # by hand
                expected_gallery_output[exp_id] = exp_models.ExpSummaryModel(
                    id=exp_model.id,
                    title=exp_model.title,
                    category=exp_model.category,
                    objective=exp_model.objective,
                    language_code=exp_model.language_code,
                    status=exp_rights_model.status,
                    community_owned=exp_rights_model.community_owned,
                    created_on=utils.get_time_in_millisecs(exp_model.created_on),
                    last_updated=utils.get_time_in_millisecs(exp_model.last_updated))

                # calling constructor for field that are not required
                # and have no default value does not work b/c
                # unspecified fields will be empty list in
                # expected_gallery_output but will be unspecified in
                # actual_gallery_output
                if exp_model.skill_tags:
                    expected_gallery_output[exp_id].skill_tags=exp_model.skill_tags,
                if exp_rights_model.owner_ids:
                    expected_gallery_output[exp_id].owner_ids = exp_rights_model.owner_ids
                if exp_rights_model.editor_ids:
                    expected_gallery_output[exp_id].editor_ids = exp_rights_model.editor_ids
                if exp_rights_model.viewer_ids:
                    expected_gallery_output[exp_id].viewer_ids = exp_rights_model.viewer_ids
                if exp_model.version:
                    expected_gallery_output[exp_id].version = exp_model.version

            # check that gallery is empty before running batch job (no realtime
            # layer at the moment)

            # run batch job
            ModifiedExpSummaryAggregator.start_computation()
            self.assertGreaterEqual(self.count_jobs_in_taskqueue(), 1)
            self.process_and_flush_pending_tasks()

            # get job output
            actual_gallery_output = ModifiedExpSummaryAggregator.get_exp_summaries()

            # check job output
            self.assertEqual(actual_gallery_output,
                             expected_gallery_output)


class OneOffReindexExplorationsJobTest(test_utils.GenericTestBase):

    EXP_ID = 'exp_id'

    def setUp(self):
        super(OneOffReindexExplorationsJobTest, self).setUp()

        explorations = [exp_domain.Exploration.create_default_exploration(
            '%s%s' % (self.EXP_ID, i), 'title %d' % i, 'category%d' % i)
            for i in xrange(5)]

        from core.domain import exp_services
        for exp in explorations:
            exp_services.save_new_exploration('owner_id', exp)
            rights_manager.publish_exploration('owner_id', exp.id)

        self.process_and_flush_pending_tasks()

    def test_standard_operation(self):
        job_id = (exp_jobs.IndexAllExplorationsJobManager.create_new())
        exp_jobs.IndexAllExplorationsJobManager.enqueue(job_id)

        self.assertEqual(self.count_jobs_in_taskqueue(), 1)

        indexed_docs = []

        def add_docs_mock(docs, index):
            indexed_docs.extend(docs)
            from core.domain import exp_services
            self.assertEqual(index, exp_services.SEARCH_INDEX_EXPLORATIONS)

        add_docs_swap = self.swap(search_services, 'add_documents_to_index', add_docs_mock)

        with add_docs_swap:
            self.process_and_flush_pending_tasks()

        ids = [doc['id'] for doc in indexed_docs]
        titles = [doc['title'] for doc in indexed_docs]
        categories = [doc['category'] for doc in indexed_docs]

        for i in xrange(5):
            self.assertIn("%s%s" % (self.EXP_ID, i), ids)
            self.assertIn('title %d' % i, titles)
            self.assertIn('category%d' % i, categories)
