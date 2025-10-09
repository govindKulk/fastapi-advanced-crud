

<details>
<summary>Python Packages and __init__.py</summary>

## Python Packages and __init__.py
1. adding __init__.py in a folder marks it as a Python package.
2. __init__.py can be empty or can execute initialization code for the package.

</details>

<details>
<summary>Python typing</summary>

## Python typing
1. use dict[str, int] instead of Dict[str, int] (from typing import Dict) in Python 3.9+, similarly for list, tuple, set.

</details>

<details>
<summary>Python Virtual Environments and Poetry</summary>

## Python Virtual Environments and Poetry
1. python -m venv env_name  # create a virtual environment
2. source env_name/bin/activate  # activate on Unix or MacOS
3. Poetry - a tool for dependency management and packaging in Python. It manages virtual environments and dependencies. 
    - poetry init  # create a new pyproject.toml file
    - poetry add package_name  # add a package to the project
    - poetry remove package_name  # remove a package from the project
    - poetry install  # install dependencies from pyproject.toml
    - poetry shell  # spawn a shell within the virtual environment
     - poetry lock  # generate or update the poetry.lock file
     - poetry publish  # publish the package to PyPI or a private repository
     - poetry build  # build the package
     - poetry update  # update dependencies to their latest versions

</details>

<details>
<summary>FastAPi commands</summary>

## FastAPi commands
- uvicorn main:app --reload  # run the FastAPI app with auto-reload
- pip install "fastapi[all]"  # install FastAPI with all optional dependencies
- pip install "fastapi[dev]"  # install FastAPI with development dependencies
- pip install "fastapi[docs]"  # install FastAPI with documentation dependencies

- FastAPI ClI commands
    - pip install fastapi-cli  # install FastAPI CLI
    - fastapi startproject project_name  # create a new FastAPI project
    - fastapi generate secret-key  # generate a secret key for the project
    - fastapi add route route_name  # add a new route to the project
    - fastapi add model model_name  # add a new model to the project
    - fastapi add router router_name  # add a new router to the project
    - fastapi add middleware middleware_name  # add a new middleware to the project
    - fastapi add dependency dependency_name  # add a new dependency to the project
    - fastapi add exception exception_name  # add a new exception handler to the project
    - fastapi add test test_name  # add a new test to the project
    - fastapi run  # run the FastAPI app

</details>

<details>
<summary>Python Decorators</summary>

## Python Decorators
1. A decorator is a function that takes another function and extends its behavior without explicitly modifying it
2. Example:
    ```python
    def my_decorator(func):
         def wrapper():
              print("Something before the function.")
              func()
              print("Something after the function.")
         return wrapper

    @my_decorator
    def say_hello():
         print("Hello!")

    say_hello()
    ```
     Output:
     ```
     Something before the function.
     Hello!
     Something after the function.
     ```
3. Important decorator functions:
    - @staticmethod: defines a static method that doesn't receive an implicit first argument (like self or cls).
    - @classmethod: defines a class method that receives the class as the first argument (cls).
    - @property: allows you to define methods in a class that can be accessed like attributes
     - @functools.wraps: a decorator for decorators that helps preserve the original function's metadata (like its name and docstring).
4. Decorators in FastAPI:
    - @app.get("/path"): defines a GET endpoint.
    - @app.post("/path"): defines a POST endpoint.
    - @app.put("/path"): defines a PUT endpoint.
    - @app.delete("/path"): defines a DELETE endpoint.
    - @app.middleware("http"): defines middleware for HTTP requests.
     - @app.exception_handler(ExceptionType): defines a custom exception handler for a specific exception type.
     - @Depends: used for dependency injection in FastAPI endpoints.

</details>

<details>
<summary># **kwargs, *args, dictionary unpacking and list unpacking</summary>

# **kwargs, *args, dictionary unpacking and list unpacking
- **kwargs allows you to pass a variable number of keyword arguments to a function. It collects them into a dictionary. its like named arguments
- *args allows you to pass a variable number of non-keyword arguments to a function.
- Dictionary unpacking: you can use ** to unpack a dictionary into keyword arguments when calling a function.
- List unpacking: you can use * to unpack a list or tuple into positional arguments when calling a function.

- My example:
```python
def func(a, b, *args, **kwargs):

  print(a)
  print(b)
  print(args)

  # Accessing tuples
  print(args[0], len(args))
  # for item in args:
     # print(item)

  # there is also tuple comprehension in python
  str_tuple = (str(item) for item in args) 
  args_str = " ".join(str_tuple)
  print(f"args_str is {args_str}")

  # tuple to list
  args_list = list(args)
  print(args_list)

  # tuple to dict
  args_dict = dict(enumerate(args))
  print(args_dict)

  # zip 
  print("zip")
  for item in zip(args, args_list):
     print(item)

  print(kwargs)

  # accessing dicts
  print(kwargs["name"])
  print(kwargs.get("age", 20))
  # print(kwargs["age"]) throws an error

  # iterating
  for key,value in kwargs.items():
     print(key, "->", value)

  # dict -> list
  print(list(kwargs.values()))
  print(list(kwargs.keys()))

values = [10,20,30,40]
key_values = {"name": "Govind"}

# unpacking
func(*values, **key_values)
```

</details>

<details>
<summary>Python args and kwargs vs JS/TS rest and spread</summary>

## python args and kwargs vs JS/TS rest and spread
## Python vs JS/TS: *args, **kwargs, Rest & Spread

Let's break down how **Python** and **JavaScript/TypeScript** handle flexible arguments, list/dict unpacking, and the rest/spread operators. We'll compare syntax, use cases, and show code examples for both languages.

***

### Python: `*args`, `**kwargs`, and Unpacking

- `*args`: Collects **positional** arguments into a tuple
- `**kwargs`: Collects **keyword** arguments into a dict
- `*` (in calls): Unpacks a list/tuple into positional arguments
- `**` (in calls): Unpacks a dict into keyword arguments

```python
# Function definition
def demo_fn(a, b, *args, **kwargs):
     print(a, b)          # Required
     print(args)          # Extra positional arguments (tuple)
     print(kwargs)        # Extra keyword arguments (dict)

# Function call
values = [1, 2, 3, 4]
extra = { 'x': 10, 'y': 20 }
demo_fn(*values, **extra)
# Output: 1 2
#         (3, 4)
#         {'x': 10, 'y': 20}
```

- **List unpacking**: `a, b, *rest = [1][2][3][4]` assigns `rest = [3]`
- **Dict unpacking**: `{**d1, **d2}` merges two dicts

***

### JS/TS: Rest and Spread operators

**Rest** (`...`) — collects multiple items into an array/object (in function parameters)
**Spread** (`...`) — unpacks an array/object into separate items (in calls or initializers)

```javascript
// Function definition with rest
function demoFn(a, b, ...args) {
  console.log(a, b);        // Required
  console.log(args);        // Extra positional arguments (array)
}

// Function call with spread
const values = [1, 2, 3, 4];
demoFn(...values); // 1 2 [3,4]

// Object spread (equiv. to Python's dict unpack)
const extra = { x: 10, y: 20 };
const merged = { a: 5, ...extra };
console.log(merged); // { a: 5, x: 10, y: 20 }
```

#### KWargs Equivalent in JS/TS
JS/TS has **no built-in kwargs**. All keyword arguments must go via an object:
```typescript
function userFn({ name, age } : { name: string; age: number }) {
  // Named arguments via object
}
userFn({ name: "Alice", age: 22 });
```

***

### Spread vs Rest: How to tell?
| Syntax      | Direction            | Python              | JS/TS                   |
|-------------|----------------------|---------------------|-------------------------|
| Spread      | Unpacks/expands      | `*` (list) / `**` (dict) in calls  | `...array` / `...obj` |
| Rest        | Collects/remains     | `*args`, `**kwargs` in definition  | `...args` (params)    |

- **Spread**: Explodes array/object into items (function calls, array/object creation, destructuring)
- **Rest**: Collects extra items into a single array/object (function parameters, destructuring)

***

### Examples: List & Dict Unpacking

**Python Lists:**
```python
# Unpack first/last and collect middle
first, *middle, last = [1,2,3,4,5]
# first=1, middle=[2,3,4], last=5
```
**JS Arrays:**
```javascript
const [first, ...middle] = [1,2,3,4,5];
const last = middle.pop(); // JS can't put ...rest in the middle
```

**Python Dicts:**
```python
d1 = {"a": 1}
d2 = {"b": 2, "c": 3}
merged = { **d1, **d2 }
```
**JS Objects:**
```javascript
const d1 = { a: 1 };
const d2 = { b: 2, c: 3 };
const merged = { ...d1, ...d2 };
```

***
</details>