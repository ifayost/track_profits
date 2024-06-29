# pull official base image
FROM python:3

# set work directory
WORKDIR /usr/src/app

# install dependencies
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . .

RUN mkdir data

CMD [ "python3", "app.py"]
