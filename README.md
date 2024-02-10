# LiODiN
Linked Open Dictionary Navigator

### Как запускать
0. (рекомендуется) Инициализировать virtual environment
```shell
python -m venv .venv
source .venv/bin/activate
```
1. Склонировать репозиторий
2. Установить нужные библиотеки
```shell
pip install -r requirements.txt
```
3. Запустить приложение
```shell
uvicorn dict_search.main:app
```

4. (если используете virtual environment)
```shell
deactivate
```