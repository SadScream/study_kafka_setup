from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError, InvalidTopicError

import sys


def kafka_check(port: int):
   """ Проверка соединения """

   consumer = KafkaConsumer(bootstrap_servers=f"localhost:{port}",
                            auto_offset_reset="earliest", consumer_timeout_ms=5000)
   print("topics: ", consumer.topics())

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