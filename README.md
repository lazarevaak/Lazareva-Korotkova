# Годовой проект 
# Чат-бот для секретаря

## Описание проекта:

Предлагается школьный чат-бот на платформе Telegram.

## Принцип работы:

Чат-бот будет работать на три фронта (секретарь, пользователи - учащиеся школы 444 и их родители, “организатор школьных мероприятий”):

### 1.	Секретарь:

      Чтобы начать диалог с ботом, школьному секретарю необходимо будет ввести служебную команду. 
      Чат-бот запросит пароль, известный только секретарю, после верного ввода пароля диалог будет открыт.
      Если пароль будет введен неверно, бот напечатает сообщение с просьбой о проверке корректности пароля. 
      Это обеспечит конфиденциальности работы секретаря. 
      Чат-бот предложит ввести команду /help, которая расскажет о документации и работе данного чат-бота.
      
#### •	Заказ справок:

      Если кто-то заказывает справку, чат-бот присылает секретарю номер заказа и готовый Word документ и спрашивает, проходит ли запрос.
      Секретарь проверяет корректность справки по официальным каналам(действительно ли такой ученик учится в школе и правильно ли введены данные). 
      Если ошибки нет, секретарь сообщает боту о том, что запрос прошел успешно и печатает справку, ставит подпись и печать. 
      Если же в данных учащегося обнаружена ошибка, бот получает сообщение об этом от секретаря. 
      Далее бот отвечает пользователю в зависимости от результата. Когда справка будет готова, секретарь печатает команду о готовности заказа и номер заказа.

#### •	Запись на прием к директору:

       От секретаря требуется работать с таблицей приемов (регулярно обновлять таблицу, заполнять свободные для посещения дни и промежутки времени). 
       Если запись отменяется со стороны директора, секретарь вводит команду, и чат-бот сообщает об этом пользователю и предлагает поменять время, ячейка в таблице удаляется.
  
### 2.	Пользователи:

Чтобы начать диалог с ботом, пользователю необходимо будет ввести /start. 
Чат-бот представится, коротко расскажет о своих возможностях и попросит представиться в ответ. 
Далее бот будет обращаться к пользователю именно так. 
Бот предложит ввести команду /help, при ее вводе пользователь получит сообщение с описанием возможных команд:

#### •	Заказ справки:

  При выборе этой команды бот попросит ввести персональные данные учащегося (ФИО, дату рождения и класс). 
  Эти данные чат-бот вставляет в шаблон справки и направляет секретарю готовый Word документ вместе с сгенерированным номером заказа. 
  Если запрос прошел успешно, бот оповещает об этом пользователя и просит подождать готовности справки. 
  Когда справка готова, бот сообщает о том, что ее можно забрать в секретариате. 
  Если запрос отклонен, бот оповещает об этом и просит проверить корректность введенных данных. 
  Для повторного ввода нужно снова выбрать заказ справки.
  
#### •	Запись на прием к директору:

  При выборе этой команды, сначала нужно ввести свои личные данные, затем бот анализирует таблицу с временем приемов, которую предварительно заполнил секретарь. 
  Сначала он предлагает дни, когда есть свободное время. После выбора дня предоставляется время. 
  В ячейку таблицы с данным днем и временем заполняются данные пользователя.
  Если директор отменил прием, бот оповестит об этом пользователя и предложит поменять время приема. 
  Если же пользователь захочет отменить прием, он должен будет ввести определенную команду. 
  Ячейка в таблице вновь станет пустой (свободной для записи).
  
#### •	Мероприятия:

  Выбрав эту команду, пользователю будет предложено подключить уведомления о предстоящих мероприятиях. 
  Если ответ будет утвердительным, чат-бот будет оповещать о новом мероприятии и в день мероприятия напоминать о нем.
  Чат-бот предложит в отдельных сообщениях информацию об актуальных мероприятиях (время, дата, ссылка на регистрацию, если это необходимо). 
  Если срок мероприятия закончился, оповещение о нем соответственно прекращается.
  
### 3.	“Организатор мероприятий”

Чтобы начать диалог с чат-ботом, данному пользователю необходимо будет ввести служебную команду. 
Чат-бот запросит пароль, известный только “организатору”, после верного ввода пароля диалог будет открыт.
Если пароль будет введен неверно, бот напечатает сообщение с просьбой о проверке корректности пароля. 
Это обеспечит конфиденциальности работы пользователя. 
Чат-бот предложит ввести команду /help, которая расскажет о документации и работе данного чат-бота.

#### •	Мероприятия:

  От “организатора мероприятий” требуется загружать информацию о предстоящих мероприятиях с указанием дат актуальности информации. 
  Для этого будет создана отдельная команда.

