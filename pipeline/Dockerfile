FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt

COPY lambda_function.py ${LAMBDA_TASK_ROOT}
COPY extract.py ${LAMBDA_TASK_ROOT}
COPY load.py ${LAMBDA_TASK_ROOT}
COPY transform.py ${LAMBDA_TASK_ROOT}

CMD [ "lambda_function.handler" ]