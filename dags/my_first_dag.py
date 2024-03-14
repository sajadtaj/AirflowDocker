from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
from random import randint

def _choose_best_model(ti):
  accuracies = ti.xcom_pull(task_ids=[
    'training_model_A',
    'training_model_B',
    'training_model_C'
  ])
  if max(accuracies) > 8:
    return 'is_accurate'
  return 'is_inaccurate'

def _training_model(model):
  print(model)
  return randint(1, 10)

with DAG("my_dag",
  start_date=datetime(2023, 1 ,1), 
  schedule_interval='@daily', 
  catchup=False):

  downloading_data = BashOperator(
    task_id='downloading_data',
    bash_command='sleep 3'
  )

  training_model_tasks = [
    PythonOperator(
      task_id=f"training_model_{model_id}",
      trigger_rule='all_success',

      python_callable=_training_model,
      op_kwargs={
        "model": model_id
      }
    ) for model_id in ['A', 'B', 'C']
  ]

  choose_best_model = BranchPythonOperator(
    task_id="choose_best_model",
    trigger_rule='none_failed',
    python_callable=_choose_best_model
  )

  accurate = BashOperator(
    task_id="accurate",
    trigger_rule='all_done',
    bash_command="echo 'accurate'"
  )

  inaccurate = BashOperator(
    task_id="inaccurate",
    trigger_rule='all_done',
    bash_command=" echo 'inaccurate'"
  )

downloading_data >> training_model_tasks >> choose_best_model >> [accurate, inaccurate]
