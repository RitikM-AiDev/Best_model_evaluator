from crewai import Crew,Task,Agent,LLM
import os
import yaml
import pandas as pd
from dotenv import load_dotenv
load_dotenv(override=True)
base_dir = os.getcwd()
config_dir = os.path.join(base_dir,"config")
agent_yml = os.path.join(config_dir,"agents.yml")
task_yml = os.path.join(config_dir,"tasks.yml")
input_file_dir = os.path.join(base_dir,"input_files")



difficulty_note = os.path.join(input_file_dir,"DifficultyNote.txt")
eval_criteria = os.path.join(input_file_dir,"EvalCriteria.txt")
expected_output_file = os.path.join(input_file_dir,"expectedOutput.txt")
golden_ans_file = os.path.join(input_file_dir,"goldenAnswer.txt")
support_requirements = os.path.join(input_file_dir,"support_requirements.txt")
task_prompt = os.path.join(input_file_dir,"taskPrompt.txt")
error_analysis_csv = os.path.join(input_file_dir,"error_analysis.csv")
model_results_csv=  os.path.join(input_file_dir,"model_results.csv")

difficulty = ''
eval_criteria_content = ''
expected_output = ''
golden_ans = ''
support_req = ''
task_prompt_text = ''
error_analysis = pd.read_csv(error_analysis_csv)
model_results = pd.read_csv(model_results_csv)

print("reading the files")
with open(difficulty_note,'r',encoding='utf-8') as file:
    difficulty = file.read()
print("read1")
with open(eval_criteria,'r',encoding='utf-8') as file:
    eval_criteria_content = file.read()
print("read2")
with open(expected_output_file,'r',encoding='utf-8') as file:
    expected_output = file.read()
print("read3")
with open(golden_ans_file,'r',encoding='utf-8') as file:
    golden_ans = file.read()
print("read4")
with open(support_requirements,'r',encoding='utf-8') as file:
    support_req = file.read()
print("read5")
with open(task_prompt,'r',encoding='utf-8') as file:
    task_prompt_text = file.read()
print("read6")



with open (agent_yml,'r') as file:
    agents = yaml.safe_load(file)
with open(task_yml,'r') as file:
    tasks = yaml.safe_load(file)


llm = LLM(
    api_key=os.getenv("GEMINI_API_KEY"),
    model="gemini-2.5-flash-lite",
    base_url="https://generativelanguage.googleapis.com/v1beta"
)
model_evaluator = Agent(
    config=agents['model_evaluator'],
    verbose=True,
    llm=llm
)

evaluation_judge = Agent(
    config=agents['evaluation_judge'],
    verbose=True,
    llm=llm
)

eval_model_config = tasks["evaluate_models"].copy()

eval_model_config["description"] += f"""
These are the reference files:
{support_req}

Task prompt:
{task_prompt_text}

Error analysis report:
{error_analysis}

Model results:
{model_results}
"""


judge_evaluation_config = tasks["judge_evaluation"].copy()

judge_evaluation_config["description"] += f"""
Golden Answer:
{golden_ans}

Evaluation criteria:
{eval_criteria_content}

Difficulty note:
{difficulty}
"""

judge_evaluation_config["expected_output"] += f"""
Reference for expected output file:
{expected_output}
"""

eval_model_task = Task(
        config=eval_model_config,
        agent=model_evaluator,
        expected_output=tasks["evaluate_models"]["expected_output"],
        output_file="model_evaluation_report.docx"
    )

eval_judge_task = Task(

        config=judge_evaluation_config,
        agent=evaluation_judge,
        output_file="model_evaluation_critique.md",
    )

crew = Crew(

    agents=[model_evaluator,evaluation_judge],
    tasks=[eval_model_task,eval_judge_task],
    verbose=True,
    process="sequential"
)
