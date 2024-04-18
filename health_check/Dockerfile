FROM public.ecr.aws/lambda/python:3.12


COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip3 install -r requirements.txt

COPY health_check.py ${LAMBDA_TASK_ROOT}

CMD [ "health_check.handler" ]
