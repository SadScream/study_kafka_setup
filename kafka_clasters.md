# Поднятие кластеров Kafka и Zookeeper в Docker

- Здесь речь пойдет о создании кластеров в докер контейнерах. Действия выполняются на виртуальной машине Ubuntu 22.04

## Установка

- следуем инструкциям по [этой ссылке](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04-ru) для установки докера. Нужно дойти до шага 3

- также нужно установить docker-compose для запуска yml инструкций

> `sudo apt install docker-compose`

- далее скачаем yml файл с инструкциями для поднятия контейнеров. Этот файл лежит в этом же репозитории и называется `docker-compose.yml`. Загрузить себе его можно следующей командой:

> `curl --silent --output docker-compose.yml https://raw.githubusercontent.com/SadScream/study_kafka_setup/main/docker-compose.yml`

(на всякий случай помещу его содержимоей в конец этого файла)

- далее в той же директории, куда скачался файл, запускаем команду

> `docker-compose up`

- эта команда начнет развертывание контейнера с Zookeeper и с 5 контейнерами Kafka: kafka1, kafka2, .., kafka5. Для отправки запросов на сервера кафки нужно использовать адрес localhost и порты в диапазоне 8091-8095

## Использование

### Подключение при помощи инструментов Kafka

- Для того, чтобы примеры подключения из этого раздела работали, нужно выполнить шаги, описанные в `kafka_local.md`. Если эти шаги не выполнялись и на хостовом компьютере не установлен Kafka, то можно перейти к следующему разделу с примерами подключения при помощи Python

- Для примера создадим топик. Для этого нужно с хоста подключиться к контейнеру и выполнить команду create. Допустим мы хотим создать топик с названием `myTopic`, подключившись к кластеру kafka1. Этот кластер расположен на порту 8091, так что команда будет выглядеть примерно таким образом:

> `cd /usr/bin`

> `kafka-topics.sh --create --topic myTopic --bootstrap-server localhost:8091 --replication-factor 1 --partitions 1`

- Отправим сообщение

```bash
kafka-console-producer.sh --broker-list localhost:8091 --topic myTopic
>hello!
>
[CTRL+C]
```

- Посмотрим список сообщений

> `kafka-console-consumer.sh --bootstrap-server localhost:8091 --topic myTopic --from-beginning --partition 0`

- Посмотрим, знает ли другой кластер об этом топике и о сообщениях, которые на нем есть. Для этого поменяем порт, например, на 8092

> `kafka-console-consumer.sh --bootstrap-server localhost:8092 --topic myTopic --from-beginning --partition 0`

### Подключение при помощи Python

- В данном репозитории есть файл `script.py`, описывающий логику создания топиков, отправки и получения сообщений при помощи python библиотеки `kafka-python`. Для установки библиотеки использовать команду

> `sudo apt -y install python3-pip`

> `pip3 install kafka-python`

- Содержимое `script.py` также на всякий случай будет продублировано внизу

## Дубликат содержимого файла `docker-compose.yml` на всякий случай

```yml
# команда запуска всех кластеров: docker-compose up
# либо docker-compose up -d kafka1 kafka2 для нескольких кластеров

version: '3.3'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest # если что-то сломается можно заменить на 6.9.1 (на кафках ниже тоже)
    ports:
    - "2181:2181"
    - "2888:2888"
    - "3888:3888"
    healthcheck:
      test: echo stat | nc localhost 2181
      interval: 10s
      timeout: 10s
      retries: 3
    environment:
    - ZOOKEEPER_SERVER_ID=1
    - ZOOKEEPER_CLIENT_PORT=2181
    - ZOOKEEPER_TICK_TIME=2000
    - ZOOKEEPER_INIT_LIMIT=5
    - ZOOKEEPER_SYNC_LIMIT=2
    - ZOOKEEPER_SERVERS=zookeeper:2888:3888
  kafka1:
    image: confluentinc/cp-kafka:latest
    depends_on:
    - zookeeper
    ports:
    - "8091:8091"
    environment:
    - KAFKA_LISTENERS=INTERNAL://0.0.0.0:9091,OUTSIDE://0.0.0.0:8091
    - KAFKA_ADVERTISED_LISTENERS=INTERNAL://kafka1:9091,OUTSIDE://localhost:8091
    - KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=INTERNAL:PLAINTEXT,OUTSIDE:PLAINTEXT
    - KAFKA_INTER_BROKER_LISTENER_NAME=INTERNAL
    - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
    - KAFKA_BROKER_ID=1
    - BOOTSTRAP_SERVERS=kafka1:9091,kafka2:9092,kafka3:9093,kafka4:9094,kafka5:9095
    - ZOOKEEPER=zookeeper:2181
  kafka2:
    image: confluentinc/cp-kafka:latest
    depends_on:
    - zookeeper
    ports:
    - "8092:8092"
    environment:
    - KAFKA_LISTENERS=INTERNAL://0.0.0.0:9092,OUTSIDE://0.0.0.0:8092
    - KAFKA_ADVERTISED_LISTENERS=INTERNAL://kafka2:9092,OUTSIDE://localhost:8092
    - KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=INTERNAL:PLAINTEXT,OUTSIDE:PLAINTEXT
    - KAFKA_INTER_BROKER_LISTENER_NAME=INTERNAL
    - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
    - KAFKA_BROKER_ID=2
    - BOOTSTRAP_SERVERS=kafka1:9091,kafka2:9092,kafka3:9093,kafka4:9094,kafka5:9095
    - ZOOKEEPER=zookeeper:2181
  kafka3:
    image: confluentinc/cp-kafka:latest
    depends_on:
    - zookeeper
    ports:
    - "8093:8093"
    environment:
    - KAFKA_LISTENERS=INTERNAL://0.0.0.0:9093,OUTSIDE://0.0.0.0:8093
    - KAFKA_ADVERTISED_LISTENERS=INTERNAL://kafka3:9093,OUTSIDE://localhost:8093
    - KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=INTERNAL:PLAINTEXT,OUTSIDE:PLAINTEXT
    - KAFKA_INTER_BROKER_LISTENER_NAME=INTERNAL
    - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
    - KAFKA_BROKER_ID=3
    - BOOTSTRAP_SERVERS=kafka1:9091,kafka2:9092,kafka3:9093,kafka4:9094,kafka5:9095
    - ZOOKEEPER=zookeeper:2181
  kafka4:
    image: confluentinc/cp-kafka:latest
    depends_on:
    - zookeeper
    ports:
    - "8094:8094"
    environment:
    - KAFKA_LISTENERS=INTERNAL://0.0.0.0:9094,OUTSIDE://0.0.0.0:8094
    - KAFKA_ADVERTISED_LISTENERS=INTERNAL://kafka4:9094,OUTSIDE://localhost:8094
    - KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=INTERNAL:PLAINTEXT,OUTSIDE:PLAINTEXT
    - KAFKA_INTER_BROKER_LISTENER_NAME=INTERNAL
    - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
    - KAFKA_BROKER_ID=4
    - BOOTSTRAP_SERVERS=kafka1:9091,kafka2:9092,kafka3:9093,kafka4:9094,kafka5:9095
    - ZOOKEEPER=zookeeper:2181
  kafka5:
    image: confluentinc/cp-kafka:latest
    depends_on:
    - zookeeper
    ports:
    - "8095:8095"
    environment:
    - KAFKA_LISTENERS=INTERNAL://0.0.0.0:9095,OUTSIDE://0.0.0.0:8095
    - KAFKA_ADVERTISED_LISTENERS=INTERNAL://kafka5:9095,OUTSIDE://localhost:8095
    - KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=INTERNAL:PLAINTEXT,OUTSIDE:PLAINTEXT
    - KAFKA_INTER_BROKER_LISTENER_NAME=INTERNAL
    - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
    - KAFKA_BROKER_ID=5
    - BOOTSTRAP_SERVERS=kafka1:9091,kafka2:9092,kafka3:9093,kafka4:9094,kafka5:9095
    - ZOOKEEPER=zookeeper:2181
```

## Дубликат содержимого `script.py`

```python
from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError, InvalidTopicError

import sys


def kafka_check(port: int):
   """ Проверка соединения """

   consumer = KafkaConsumer(bootstrap_servers=f"localhost:{port}",
                            auto_offset_reset="earliest", consumer_timeout_ms=5000)
   print("topics: ", consumer.topics())
   print(consumer.topics())

   if consumer is None:
      print("Что то пошло не так..")
      return False, consumer

   elif len(consumer.topics()) == 0:
      print("Отсутствуют топики")
      return False, consumer

   else:
      print("Соединение установлено!")

      # если на этом моменте скрипт зависает, то, возможно, есть проблема с OUTSIDE портами в композ файле 
      print("Доступные топики: ", consumer.topics())
      
      return True, consumer


def kafka_check_topic(consumer: KafkaConsumer, topic: str):
   """ Проверка доступности топика для консьюмера """

   topic_in_topics = topic in consumer.topics()
   print("Виден ли топик консьюмеру: ", "виден" if topic_in_topics else "не виден")

   return topic_in_topics


def kafka_send_message(port: int, messages: list[str], topic: str, wait_every=True):
   producer = KafkaProducer(bootstrap_servers=f"localhost:{port}")

   for line in messages:
      future = producer.send(topic, line.encode("utf-8")) # асинхронная операция

      if wait_every:
         record_metadata = future.get(timeout=10) # делаем синхронный вызов получения результата отправки

   if not wait_every:
      record_metadata = future.get(timeout=5)
      print("Метаданные последнего сообщения: topic: {} patition: {} offset: {}".format(
            record_metadata.topic, record_metadata.partition, record_metadata.offset))

   return


def kafka_recieve_message(port: int, topic_out: str):
   consumer = KafkaConsumer(topic_out,
                            bootstrap_servers=f"localhost:{port}",
                            auto_offset_reset="earliest", consumer_timeout_ms=5000)
   results = []

   for msg in consumer:
      results.append(msg.value)

   return results


def kafka_create_topic(port: int, name: str, num_partitions: int = 1, replication_factor: int = 1):
    admin_client = KafkaAdminClient(bootstrap_servers=f"localhost:{port}")

    topic_list = []
    topic_list.append(NewTopic(name=name, num_partitions=num_partitions, replication_factor=replication_factor))

    try:
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
    except TopicAlreadyExistsError:
        print("Топик уже существует, будет использован существующий")
        return True
    except InvalidTopicError:
        print("Неправильное имя топика. Можно использовать символы a-z A-Z 0-9 . _ -")
        return False
    except Exception as e:
        print("Неизвестная ошибка")
        print(e)
        return False
    
    return True


ports = [8091, 8092, 8093]
topic = "firstTopic"

for port in ports:
    messages = [
        f"hello, kafka on port {port}",
    ]

    print("Результаты для порта ", port)
    _result, consumer = kafka_check(port)

    if not _result:
        sys.exit(0)

    _result = kafka_create_topic(port, topic)

    if not _result:
        sys.exit(0)

    _result = kafka_check_topic(consumer, topic)

    if not _result:
        sys.exit(0)

    kafka_send_message(port, messages, topic)

    messages = kafka_recieve_message(port, topic)
    print(messages)

    print("\n\n")
```
