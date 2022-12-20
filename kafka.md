# Администрирование Kafka и Zookeeper

## Установка

> `sudo apt update`

- Под капотом кафка использует JVM, так что устанавливаем ее

> `sudo apt install default-jdk`

- Проверяем, установилось ли

> `java --version`

- Устанавливаем curl

> `sudo apt install curl`

- Скачиваем архив

> `curl -O https://downloads.apache.org/kafka/3.3.1/kafka_2.13-3.3.1.tgz`

- Распаковываем

> `tar -xzf kafka_2.13-3.3.1.tgz`

- Переместить в папку kafka

> `sudo mv kafka_2.13-3.3.1 /usr/local/kafka`

- Затем нужно нужно обернуть приложение как сервис

> `cd /etc/systemd/system/`

> `sudo nano zookeeper.service`

```bash
[Unit]
Description=Zookeeper server
Requires=network.target remote-fs.target
After=network.target remote-fs.target

[Service]
Type=simple
ExecStart=/usr/local/kafka/bin/zookeeper-server-start.sh /usr/local/kafka/config/zookeeper.properties
ExecStop=/usr/local/kafka/bin/zookeeper-server-stop.sh
Restart=on-abnormal

[Install]
WantedBy=multi-user.target
```

`Ctrl+S Ctrl+X`

- Получить путь к java development kit

> `update-alternatives --list java`

выход будет примерно таким:

> /usr/lib/jvm/java-11-openjdk-amd64/bin/java

нам нужна только эта часть: `/usr/lib/jvm/java-11-openjdk-amd64`

- далее

> `sudo nano kafka.service`

```bash
[Unit]
Description=Apache Kafka Server
Requires=zookeeper.service

[Service]
Type=simple
Environment="JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64"
ExecStart=/usr/local/kafka/bin/kafka-server-start.sh /usr/local/kafka/config/server.properties
ExecStop=/usr/local/kafka/bin/kafka-server-stop.sh

[Install]
WantedBy=multi-user.target
```

`Ctrl+S Ctrl+X`

- Перезагрузить systemd daemon

> `sudo systemctl daemon-reload`

## Запуск сервисок Zookeeper и Kafka

> `sudo systemctl start zookeeper`

> `sudo systemctl start kafka`

- Проверить статус сервисов

> `sudo systemctl status zookeeper`

вывод должен быть примерно такой

```
● zookeeper.service - Zookeeper server

     Loaded: loaded (/etc/systemd/system/zookeeper.service; disabled; vendor preset: enabled)

     Active: active (running)
```

аналогично

> `sudo systemctl status kafka`

## Использование

- Для начала добавить путь к Каффка в bash

> `export PATH=/usr/local/kafka/bin:$PATH`

- Создание топика

> `kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic firstTopic`

```
Опции:
--create - указываем, что нужно создать топик
--bootstrap-server - сервер, к которому нужно подключиться. Локально кафка слушает 9092 и 9091 (без шифрования) порты
--partitions - количество партиций
--replication-factor - количество копий партиций. Т.к. у нас один брокер, то смысла ставить больше 1 нет
--topic - название топика
```

если ловим ошибку
```
WARN [AdminClient clientId=adminclient-1] Connection to node -1 (localhost/127.0.0.1:9092) could not be established. Broker may not be available.
```
то еще раз проверяем статус кафки

> `sudo systemctl status kafka`

если статус inactive, то запускаем сервис заново

> `sudo systemctl start kafka`

- Если все нормально и вышло сообщение `Created topic firstTopic.`, то можно попробовать вывести список имеющихся топиков

> `kafka-topics.sh --list --bootstrap-server localhost:9092`

## Отправка и получение сообщений

- Откройте второй терминал (но не закрывайте первый). В новом терминале введите

> `export PATH=/usr/local/kafka/bin:$PATH`

- Теперь в первом терминале введите команду ниже, чтобы запустить иммитацию продьюсера

> `kafka-console-producer.sh --broker-list localhost:9092 --topic firstTopic`

- Во втором терминале введите команду запуска иммитации консьюмера

> `kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic firstTopic --from-beginning`

Введите какой-нибудь текст в первом терминале и нажмите enter. Вводимые сообщения будут отображаться во втором терминале

## Использование Kafka с python3

- установить pip3

> `sudo apt install python3-pip`

- установить kafka

> `pip install kafka-python`

- создать python скрипт

> `cd ~/Desktop/`

> `mkdir py-kafka`

> `cd py-kafka/`

> `nano script.py`

```python
from kafka import KafkaConsumer, KafkaProducer

def kafka_check():
   """ Проверка соединения """

   consumer = KafkaConsumer(bootstrap_servers='localhost:9092',
                            auto_offset_reset='earliest', consumer_timeout_ms=5000)

   if consumer is None:
      print("Что то пошло не так..")
      return False, consumer

   elif len(consumer.topics()) == 0:
      print("Отсутствуют топики")
      return False, consumer

   else:
      return True, consumer

def kafka_check_topic(consumer, topic):
   """ Проверка доступности топика для консьюмера """

   topic_in_topics = topic in consumer.topics()
   print("топик виден консьюмеру: ", "виден" if topic_in_topics else "не виден")

   return topic_in_topics

def kafka_send_message(messages, topic, wait_every=True):
   producer = KafkaProducer(bootstrap_servers='localhost:9092')

   for line in messages:
      future = producer.send(topic, line.encode('utf-8')) # асинхронная операция

      if wait_every:
         record_metadata = future.get(timeout=5) # делаем синхронный вызов получения результата отправки

   if not wait_every:
      record_metadata = future.get(timeout=5)
      print("Метаданные последнего сообщения: topic: {} patition: {} offset: {}".format(
            record_metadata.topic, record_metadata.partition, record_metadata.offset))

   return

def kafka_recieve_message(topic_out):
   consumer = KafkaConsumer(topic_out,
                            bootstrap_servers='localhost:9092',
                            auto_offset_reset='earliest', consumer_timeout_ms=5000)
   results = []

   for msg in consumer:
      results.append(msg.value)

   return results

messages = [
   "hello",
   "this is my first message via python"
]
topic = "firstTopic"

_result, consumer = kafka_check()

if not _result:
   import sys
   sys.exit(0)

_result = kafka_check_topic(consumer, topic)

if not _result:
   import sys
   sys.exit(0)

kafka_send_message(messages, topic)
messages = kafka_recieve_message(topic)
print(messages)
```