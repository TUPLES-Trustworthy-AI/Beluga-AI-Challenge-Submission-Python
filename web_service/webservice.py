import os
import zipfile
import shutil
import logging
from flask import Flask, request, send_file, jsonify
from src.business_logic import CompetitorModelBusinessLogic

app = Flask(__name__)

# Base path for executions
BASE_PATH = os.path.join('..', 'res', 'executions')

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

logger = logging.getLogger(__name__)

logging.disable(logging.DEBUG)

# Build the business logic object
competitor_logic = CompetitorModelBusinessLogic()

@app.route('/explain', methods=['POST'])
def explain():
    """
    Endpoint to handle the explainer process for a submission and plan.
    """
    logger.info(f"[EXPLAIN REQUEST] - Received /explain request with query parameters: {request.args}")

    # Extract query parameters
    submission_id = request.args.get('submission_id')
    plan_id = request.args.get('plan_id')

    if not submission_id or not plan_id:
        logger.error(f"[EXPLAIN REQUEST] - Missing required query parameters: submission_id or plan_id")
        return jsonify({"error": "Missing required query parameters"}), 400

    # Define paths for input, output, and temporary files
    execution_path = os.path.join(BASE_PATH, submission_id, "explain", plan_id)
    input_path = os.path.join(execution_path, 'input')
    output_path = os.path.join(execution_path, 'output')
    temp_path = os.path.join(execution_path, 'temp')

    # Create directories if they don't exist
    os.makedirs(input_path, exist_ok=True)
    os.makedirs(output_path, exist_ok=True)
    os.makedirs(temp_path, exist_ok=True)
    logger.info(f"[EXPLAIN REQUEST] - Directories set up: input={input_path}, output={output_path}, temp={temp_path}")

    try:
        # Check content type for zip file
        if request.content_type != 'application/octet-stream':
            logger.error(
                f"[EXPLAIN REQUEST] - Invalid content type: {request.content_type}. Expected application/octet-stream.")
            return jsonify({"error": "Invalid content-type. Expected application/octet-stream"}), 400

        # Save the uploaded zip file from request body
        logger.info(f"[EXPLAIN REQUEST] - Receiving zip file from request body.")
        zip_file = request.data
        zip_file_path = os.path.join(temp_path, 'uploaded.zip')

        with open(zip_file_path, 'wb') as f:
            f.write(zip_file)
        logger.info(f"[EXPLAIN REQUEST] - Zip file saved to: {zip_file_path}")

        # Unzip the file
        unzip_file(zip_file_path, input_path)

        # Call business logic for the explain process
        logger.info(
            f"[EXPLAIN REQUEST] - Calling business logic for explain. Submission ID: {submission_id}, Plan ID: {plan_id}")
        competitor_logic = CompetitorModelBusinessLogic()
        competitor_logic.explain(submission_id, plan_id, input_path, output_path)
        logger.info(
            f"[EXPLAIN REQUEST] - Business logic completed for Submission ID: {submission_id}, Plan ID: {plan_id}")

        # Zip the output directory
        output_zip = zip_directory(output_path, os.path.join(temp_path, "output"))

        # Send the zipped output file as the response
        logger.info(f"[EXPLAIN REQUEST] - Sending zipped output: {output_zip}")
        return send_file(output_zip, as_attachment=True, mimetype='application/octet-stream')

    except Exception as e:
        logger.error(f"[EXPLAIN REQUEST] - Error occurred during explaining process: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/plan', methods=['POST'])
def plan():
    """
    Endpoint to handle the planning process for a submission and problem.
    """
    logger.debug(f"[PLAN REQUEST] - Received /plan request with query parameters: {request.args}")

    # Extract query parameters
    submission_id = request.args.get('submission_id')
    problem_id = request.args.get('problem_id')

    if not submission_id or not problem_id:
        logger.error(f"[PLAN REQUEST] - Missing required query parameters: submission_id or problem_id")
        return jsonify({"error": "Missing required query parameters"}), 400

    # Define paths for input, output, and temporary files
    execution_path = os.path.join(BASE_PATH, submission_id, "problems", problem_id)
    input_path = os.path.join(execution_path, 'input')
    output_path = os.path.join(execution_path, 'output')
    temp_path = os.path.join(execution_path, 'temp')

    # Create directories if they don't exist
    os.makedirs(input_path, exist_ok=True)
    os.makedirs(output_path, exist_ok=True)
    os.makedirs(temp_path, exist_ok=True)
    logger.debug(f"[PLAN REQUEST] - Directories set up: input={input_path}, output={output_path}, temp={temp_path}")

    try:
        # Check content type for zip file
        if request.content_type != 'application/octet-stream':
            logger.error(
                f"[PLAN REQUEST] - Invalid content type: {request.content_type}. Expected application/octet-stream.")
            return jsonify({"error": "Invalid content-type. Expected application/octet-stream"}), 400

        # Save the uploaded zip file from request body
        logger.debug(f"[PLAN REQUEST] - Receiving zip file from request body.")
        zip_file = request.data
        zip_file_path = os.path.join(temp_path, 'uploaded.zip')

        with open(zip_file_path, 'wb') as f:
            f.write(zip_file)
        logger.debug(f"[PLAN REQUEST] - Zip file saved to: {zip_file_path}")

        # Unzip the file
        unzip_file(zip_file_path, input_path)

        # Call business logic for the plan process
        logger.debug(
            f"[PLAN REQUEST] - Calling business logic for plan. Submission ID: {submission_id}, Problem ID: {problem_id}")
        # competitor_logic = CompetitorModelBusinessLogic()
        competitor_logic.plan(submission_id, problem_id, input_path, output_path)
        logger.debug(
            f"[PLAN REQUEST] - Business logic completed for Submission ID: {submission_id}, Problem ID: {problem_id}")

        # Zip the output directory
        output_zip = zip_directory(output_path, os.path.join(temp_path, "output"))

        # Send the zipped output file as the response
        logger.debug(f"[PLAN REQUEST] - Sending zipped output: {output_zip}")
        return send_file(output_zip, as_attachment=True, mimetype='application/octet-stream')

    except Exception as e:
        logger.error(f"[PLAN REQUEST] - Error occurred during planning process: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/setup', methods=['POST'])
def setup():
    """
    Endpoint to handle setup for a submission.
    """
    logger.debug(f"[SETUP REQUEST] - Received /setup request with query parameters: {request.args}")

    # Extract query parameters
    submission_id = request.args.get('submission_id')

    if not submission_id:
        logger.error(f"[SETUP REQUEST] - Missing required query parameter: submission_id")
        return jsonify({"error": "Missing required query parameter: submission_id"}), 400

    try:
        # Call setup business logic
        logger.debug(f"[SETUP REQUEST] - Calling setup business logic for Submission ID: {submission_id}")
        # competitor_logic = CompetitorModelBusinessLogic()
        competitor_logic.setup(submission_id)
        logger.debug(f"[SETUP REQUEST] - Setup completed for Submission ID: {submission_id}")

        return jsonify({"message": "Setup completed successfully"}), 200

    except Exception as e:
        logger.error(f"[SETUP REQUEST] - Error occurred during setup process: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/setup_problem', methods=['POST'])
def setup_problem():
    """
    Endpoint to handle the setup process for a submission and problem.
    """
    logger.debug(f"[SETUP PROBLEM REQUEST] - Received /setup_problem request with query parameters: {request.args}")

    # Extract query parameters
    submission_id = request.args.get('submission_id')
    problem_id = request.args.get('problem_id')

    if not submission_id or not problem_id:
        logger.error(f"[SETUP PROBLEM REQUEST] - Missing required query parameters: submission_id or problem_id")
        return jsonify({"error": "Missing required query parameters"}), 400

    # Define paths for input, output, and temporary files
    execution_path = os.path.join(BASE_PATH, submission_id, "problems", problem_id)
    input_path = os.path.join(execution_path, 'input')
    output_path = os.path.join(execution_path, 'output')
    temp_path = os.path.join(execution_path, 'temp')

    # Create directories if they don't exist
    os.makedirs(input_path, exist_ok=True)
    os.makedirs(output_path, exist_ok=True)
    os.makedirs(temp_path, exist_ok=True)
    logger.debug(f"[SETUP PROBLEM REQUEST] - Directories set up: input={input_path}, output={output_path}, temp={temp_path}")

    try:
        # Check content type for zip file
        if request.content_type != 'application/octet-stream':
            logger.error(f"[SETUP PROBLEM REQUEST] - Invalid content type: {request.content_type}. Expected application/octet-stream.")
            return jsonify({"error": "Invalid content-type. Expected application/octet-stream"}), 400

        # Save the uploaded zip file from request body
        logger.debug(f"[SETUP PROBLEM REQUEST] - Receiving zip file from request body.")
        zip_file = request.data
        zip_file_path = os.path.join(temp_path, 'uploaded.zip')

        with open(zip_file_path, 'wb') as f:
            f.write(zip_file)
        logger.debug(f"[SETUP PROBLEM REQUEST] - Zip file saved to: {zip_file_path}")

        # Unzip the file
        unzip_file(zip_file_path, input_path)

        # Call business logic for the setup process
        logger.debug(f"[SETUP PROBLEM REQUEST] - Calling business logic for setup. Submission ID: {submission_id}, Problem ID: {problem_id}")
        # competitor_logic = CompetitorModelBusinessLogic()
        competitor_logic.setup_problem(submission_id, problem_id, input_path)
        logger.debug(f"[SETUP PROBLEM REQUEST] - Business logic completed for Submission ID: {submission_id}, Problem ID: {problem_id}")

        # Return a simple 200 status
        return jsonify({"message": "Setup Problem completed successfully"}), 200

    except Exception as e:
        logger.error(f"[SETUP PROBLEM REQUEST] - Error occurred during setup process: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/start_simulation', methods=['POST'])
def start_simulation():
    """
    Endpoint to start a simulation.
    """
    logger.debug(
        f"[START SIMULATION REQUEST] - Received /start_simulation request with query parameters: {request.args}")

    # Extract query parameters
    submission_id = request.args.get('submission_id')
    problem_id = request.args.get('problem_id')
    simulation_id = request.args.get('simulation_id')

    if not submission_id or not problem_id or not simulation_id:
        logger.debug(
            "[START SIMULATION REQUEST] - Missing required query parameters: submission_id, problem_id, or simulation_id")
        return jsonify({"error": "Missing required query parameters"}), 400

    try:
        # Call business logic for start_simulation
        logger.debug(
            f"[START SIMULATION REQUEST] - Calling business logic for start_simulation. Submission ID: {submission_id}, Problem ID: {problem_id}, Simulation ID: {simulation_id}")
        # competitor_logic = CompetitorModelBusinessLogic()
        competitor_logic.start_simulation(submission_id, problem_id, simulation_id)
        logger.debug(
            f"[START SIMULATION REQUEST] - Simulation started successfully for Submission ID: {submission_id}, Problem ID: {problem_id}, Simulation ID: {simulation_id}")

        return jsonify({"message": "Simulation started successfully"}), 200

    except Exception as e:
        logger.error(f"[START SIMULATION REQUEST] - Error occurred during simulation start: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/next_action', methods=['POST'])
def next_action():
    """
    Endpoint to handle the next action process for a submission, problem, simulation, and action.
    """
    logger.debug(f"[NEXT ACTION REQUEST] - Received /next_action request with query parameters: {request.args}")

    # Extract query parameters
    submission_id = request.args.get('submission_id')
    problem_id = request.args.get('problem_id')
    simulation_id = request.args.get('simulation_id')
    action_id = request.args.get('action_id')

    # Validate that all parameters are present
    if not submission_id or not problem_id or not simulation_id or not action_id:
        logger.error(f"[NEXT ACTION REQUEST] - Missing required query parameters: submission_id, problem_id, simulation_id, or action_id")
        return jsonify({"error": "Missing required query parameters"}), 400

    # Define paths for input, output, and temporary files
    execution_path = os.path.join(BASE_PATH, submission_id, "problems", problem_id, "simulations", simulation_id, "actions", action_id)
    input_path = os.path.join(execution_path, 'input')
    output_path = os.path.join(execution_path, 'output')
    temp_path = os.path.join(execution_path, 'temp')

    # Create directories if they don't exist
    os.makedirs(input_path, exist_ok=True)
    os.makedirs(output_path, exist_ok=True)
    os.makedirs(temp_path, exist_ok=True)
    logger.debug(f"[NEXT ACTION REQUEST] - Directories set up: input={input_path}, output={output_path}, temp={temp_path}")

    try:
        # Check content type for zip file
        if request.content_type != 'application/octet-stream':
            logger.error(
                f"[NEXT ACTION REQUEST] - Invalid content type: {request.content_type}. Expected application/octet-stream.")
            return jsonify({"error": "Invalid content-type. Expected application/octet-stream"}), 400

        # Save the uploaded zip file from request body
        logger.debug(f"[NEXT ACTION REQUEST] - Receiving zip file from request body.")
        zip_file = request.data
        zip_file_path = os.path.join(temp_path, 'uploaded.zip')

        with open(zip_file_path, 'wb') as f:
            f.write(zip_file)
        logger.debug(f"[NEXT ACTION REQUEST] - Zip file saved to: {zip_file_path}")

        # Unzip the file
        unzip_file(zip_file_path, input_path)

        # Call business logic for the next action process
        logger.debug(
            f"[NEXT ACTION REQUEST] - Calling business logic for next action. Submission ID: {submission_id}, Problem ID: {problem_id}, Simulation ID: {simulation_id}, Action ID: {action_id}")
        # competitor_logic = CompetitorModelBusinessLogic()
        competitor_logic.next_action(submission_id, problem_id, simulation_id, action_id, input_path, output_path)
        logger.debug(
            f"[NEXT ACTION REQUEST] - Business logic completed for Submission ID: {submission_id}, Problem ID: {problem_id}, Simulation ID: {simulation_id}, Action ID: {action_id}")

        # Zip the output directory
        output_zip = zip_directory(output_path, os.path.join(temp_path, "output"))

        # Send the zipped output file as the response
        logger.debug(f"[NEXT ACTION REQUEST] - Sending zipped output: {output_zip}")
        return send_file(output_zip, as_attachment=True, mimetype='application/octet-stream')

    except Exception as e:
        logger.error(f"[NEXT ACTION REQUEST] - Error occurred during next action process: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


def unzip_file(zip_file_path, extract_to):
    """
    Unzips the file from the given zip_file_path into the extract_to directory.
    """
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        logging.debug(f"Unzipped file to {extract_to}")
    except zipfile.BadZipFile:
        logging.error(f"Error: The file {zip_file_path} is not a valid zip file.")
        raise

def zip_directory(directory_path, output_zip_path):
    """
    Zips the content of a directory and saves it as a zip file in the output_zip_path.
    """
    try:
        shutil.make_archive(output_zip_path, 'zip', directory_path)
        logging.debug(f"Zipping output from {output_zip_path}")
        return f"{output_zip_path}.zip"
    except Exception as e:
        logging.error(f"Error: Failed to zip directory {directory_path}. Exception: {str(e)}")
        raise


if __name__ == '__main__':
    logger.info("Starting Flask application.")
    app.run(host='0.0.0.0', port=80, debug=True)
