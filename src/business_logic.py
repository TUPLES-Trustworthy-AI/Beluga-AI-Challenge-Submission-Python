import os, time, logging

# Add the tools directory to the path, to ensure consistent import names
import sys
sys.path.insert(0, os.path.join('/app', 'src', 'tools'))

import json
from beluga_lib.beluga_problem import BelugaProblemDecoder
from beluga_lib.problem_state import BelugaProblemState
from evaluation.planner_api import BelugaPlan, ProbabilisticPlanningMetatada

# SECTION TO BE EDITED BY THE COMPETITORS ===================================

# Import the planning implementation
# NOTE in this template we build both a deterministc and and a probabilistic
# (trivial) planner. In practice only oe solution is needed
from evaluation.planner_examples import RandomProbabilisticPlanner
from evaluation.planner_examples import RandomDeterministicPlanner

# END OF SECTION TO BE EDITED BY THE COMPETITORS ============================

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

logger = logging.getLogger(__name__)

logging.disable(logging.DEBUG)

class Configuration:
    def __init__(self):
        self.problem_file_name = 'problem.json'
        self.plan_file_name = 'plan.json'
        self.state_and_metadata_name = 'state_and_metadata.json'
        self.action_file_name = 'action.json'

configuration = Configuration()

class CompetitorModelBusinessLogic:

    def __init__(self):
        # SECTION TO BE EDITED BY THE COMPETITORS ===================================

        # Build the deterministc planner
        # NOTE the web service code relies on the det_planner variable for the
        # deterministc API, so do not change that name.
        self.det_planner = RandomDeterministicPlanner(max_steps=30)

        # Build the deterministc planner
        # NOTE the web service code relies on the prob_planner variable for the
        # deterministc API, so do not change that name.
        self.prob_planner = RandomProbabilisticPlanner()

        # END OF THE SECTION TO BE EDITED BY THE COMPETITORS ========================

    def explain(self, submission_id, plan_id, input_path, output_path):
        """
        Business logic for processing input files and generating output.
        """
        logger.info(f"[EXPLAIN] - Start processing - Submission ID: {submission_id}, Plan ID: {plan_id}")
        logger.info(f"[EXPLAIN] - Input path: {input_path}, Output path: {output_path}")

        try:
            # SECTION TO BE EDITED BY THE COMPETITORS ===================================

            # Generate an example output file (this should be replaced with actual logic)
            output_file = os.path.join(output_path, f"output_{plan_id}.txt")
            logger.info(f"[EXPLAIN] - Preparing to write output file: {output_file}")
            with open(output_file, 'w') as f:
                f.write(f"Explanation generated for submission {submission_id}, plan {plan_id}\n")

            # Simulating a delay in processing (15 seconds)
            logger.info(f"[EXPLAIN] - Processing... ")
            time.sleep(2)

            # END OF THE SECTION TO BE EDITED BY THE COMPETITORS ========================

            logger.info(f"[EXPLAIN] - Completed processing - Submission ID: {submission_id}, Plan ID: {plan_id}")

            return True

        except Exception as e:
            logger.error(f"[EXPLAIN] - Error during execution for Submission ID: {submission_id}, Plan ID: {plan_id}: {str(e)}", exc_info=True)
            return False


    def plan(self, submission_id, problem_id, input_path, output_path):
        """
        Business logic for processing input files and generating output.
        """
        logger.debug(f"[PLAN] - Start processing - Submission ID: {submission_id}, Problem ID: {problem_id}")
        logger.debug(f"[PLAN] - Input path: {input_path}, Output path: {output_path}")

        try:
            # Read the problem data
            input_file = os.path.join(input_path, configuration.problem_file_name)
            logger.debug(f"[PLAN] - Preparing to read input file: {input_file}")
            with open(input_file) as fp:
                prb = json.load(fp, cls=BelugaProblemDecoder)
            logger.debug(f"[PLAN] - Completed reading - Submission ID: {submission_id}, Problem ID: {problem_id}")

            # Call the planning method
            logger.debug(f"[PLAN] - Processing...")
            plan = self.det_planner.build_plan(prb)
            # Null plans are considered the same as emtpy plans
            if plan is None:
                plan = BelugaPlan()
            logger.debug(f"[PLAN] - Completed processing - Submission ID: {submission_id}, Problem ID: {problem_id}")

            # Generate output file
            output_file = os.path.join(output_path, configuration.plan_file_name)
            logger.debug(f"[PLAN] - Preparing to write output file: {output_file}")
            with open(output_file, 'w') as fp:
                json.dump(plan.to_json_obj(), fp)
            logger.debug(f"[PLAN] - Completed writing - Submission ID: {submission_id}, Problem ID: {problem_id}")

            return True

        except Exception as e:
            logger.error(f"[PLAN] - Error during execution for Submission ID: {submission_id}, Problem ID: {problem_id}: {str(e)}", exc_info=True)
            return False

    def setup(self, submission_id):
        """
        Setup method for initializing resources or configurations for the submission.
        """
        logger.debug(f"[SETUP] - Start setup - Submission ID: {submission_id}")

        self.det_planner.setup()

        # time.sleep(15)
        logger.debug(f"[SETUP] - Setup complete - Submission ID: {submission_id}")

    def setup_problem(self, submission_id, problem_id, input_path):
        """
        Setup method for initializing resources or configurations specific to a problem within the submission.
        """
        logger.debug(f"[SETUP PROBLEM] - Start problem setup - Submission ID: {submission_id}, Problem ID: {problem_id}")

        try:
            # Read the problem data
            input_file = os.path.join(input_path, f'problem.json')
            logger.debug(f"[SETUP PROBLEM] - Preparing to read input file: {input_file}")
            with open(input_file) as fp:
                prb = json.load(fp, cls=BelugaProblemDecoder)
            logger.debug(f"[SETUP PROBLEM] - Completed reading - Submission ID: {submission_id}, Problem ID: {problem_id}")

            # Setup the planner for the problem
            logger.debug(f"[SETUP PROBLEM] - Processing... Simulating a 15-second delay")
            self.prob_planner.setup(prb)
            logger.debug(f"[SETUP PROBLEM] - Problem setup complete - Submission ID: {submission_id}, Problem ID: {problem_id}")

        except Exception as e:
            logger.error(f"[SETUP PROBLEM] - Error during problem setup for Submission ID: {submission_id}, Problem ID: {problem_id}: {str(e)}", exc_info=True)
            return False

    def start_simulation(self, submission_id, problem_id, simulation_id):
        """
        Start a simulation process for a given submission, problem, and simulation ID.
        """

        # Setup the simulation
        logger.debug(f"[START SIMULATION] - Simulation setup started - Submission ID: {submission_id}, Problem ID: {problem_id}, Simulation ID: {simulation_id}")
        self.prob_planner.setup_episode()
        logger.debug(f"[START SIMULATION] - Simulation setup complete - Submission ID: {submission_id}, Problem ID: {problem_id}, Simulation ID: {simulation_id}")

    def next_action(self, submission_id, problem_id, simulation_id, action_id, input_path, output_path):
        """
        Handle the next action in a series for a specific simulation.
        """

        try:
            # Read the state and metadata
            input_file = os.path.join(input_path, configuration.state_and_metadata_name)
            logger.debug(f"[NEXT ACTION] - Preparing to read input file: {input_file} - Submission ID: {submission_id}, Problem ID: {problem_id}, Simulation ID: {simulation_id}, Action ID: {action_id}")
            with open(input_file) as fp:
                data = json.load(fp)
                state = BelugaProblemState.from_json_obj(data['state'], self.prob_planner.prb)
                metadata = ProbabilisticPlanningMetatada.from_json_obj(data['metadata'])

            # Retrieve the next action
            ba = self.prob_planner.next_action(state, metadata)

            # Generate the output file
            output_file = os.path.join(output_path, configuration.action_file_name)
            logger.debug(f"[NEXT ACTION] - Preparing to write output file: {output_file} - Submission ID: {submission_id}, Problem ID: {problem_id}, Simulation ID: {simulation_id}, Action ID: {action_id}")
            with open(output_file, 'w') as fp:
                json.dump(ba.to_json_obj(), fp)
            logger.debug(f"[NEXT ACTION] - Completed writing - Submission ID: {submission_id}, Problem ID: {problem_id}, Simulation ID: {simulation_id}, Action ID: {action_id}")

            return True

        except Exception as e:
            logger.error(f"[NEXT ACTION] - Error during execution for Submission ID: {submission_id}, Problem ID: {problem_id}, Simulation ID: {simulation_id}, Action ID: {action_id}: {str(e)}", exc_info=True)
            return False
