# Python QTest Library

A client library to interact with the qTest API, which one can reference here: [api.qasymphony.com](https://api.qasymphony.com/)

## Usage

```python
from qtest import qtest

qtest = qtest.QTestClient(username="username@yourco.com", password="password", site_name="yourco")
all_projects = qtest.get_projects()
project_names = [project['name'] for project in all_projects]
print(project_names)
```