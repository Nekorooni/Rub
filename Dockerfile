FROM gorialis/discord.py:alpine-rewrite-extras

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "./rub.py" ]