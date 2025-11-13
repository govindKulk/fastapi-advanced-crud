# Python Type Hints: Comprehensive Guide

## Table of Contents
1. [Introduction to Type Hints](#1-introduction-to-type-hints)
2. [Basic Types](#2-basic-types)
3. [Collection Types](#3-collection-types)
4. [Optional and Union Types](#4-optional-and-union-types)
5. [Type Aliases](#5-type-aliases)
6. [Callable Types](#6-callable-types)
7. [Generic Types and TypeVar](#7-generic-types-and-typevar)
8. [Protocol and Structural Subtyping](#8-protocol-and-structural-subtyping)
9. [Literal Types](#9-literal-types)
10. [TypedDict](#10-typeddict)
11. [Advanced Generic Patterns](#11-advanced-generic-patterns)
12. [Type Narrowing](#12-type-narrowing)
13. [Escape Hatches and Workarounds](#13-escape-hatches-and-workarounds)
14. [Best Practices](#14-best-practices)

---

## 1. Introduction to Type Hints

### What Are Type Hints?
Type hints are annotations that specify the expected types of variables, function parameters, and return values. Introduced in Python 3.5 (PEP 484), they:
- **Don't affect runtime behavior** - Python remains dynamically typed
- **Enable static type checking** - Tools like mypy, pyright, pylance catch errors before runtime
- **Improve code documentation** - Types make intent clearer
- **Enhance IDE support** - Better autocomplete and refactoring

### Why Use Type Hints?
```python
# Without types - unclear what's expected
def process_data(data):
    return data.upper()

# With types - clear contract
def process_data(data: str) -> str:
    return data.upper()
```

### Type Checkers
- **mypy** - Original type checker, most mature
- **pyright** - Fast, used by VS Code (Pylance)
- **pyre** - Facebook's type checker
- **pytype** - Google's type checker

---

## 2. Basic Types

### Primitive Types
```python
# Built-in types
name: str = "Alice"
age: int = 30
height: float = 5.8
is_active: bool = True
nothing: None = None

# Type annotations without assignment
name: str
age: int

# Function annotations
def greet(name: str) -> str:
    return f"Hello, {name}"

def log_message(msg: str) -> None:  # None means no return value
    print(msg)
```

### Bytes and ByteArray
```python
from typing import ByteString

data: bytes = b"hello"
mutable_data: bytearray = bytearray(b"world")
any_bytes: ByteString = b"generic"  # Accepts bytes, bytearray, memoryview
```

---

## 3. Collection Types

### Lists, Tuples, Sets, Dicts
```python
from typing import List, Tuple, Set, Dict

# Lists - homogeneous collections
numbers: List[int] = [1, 2, 3]
names: list[str] = ["Alice", "Bob"]  # Python 3.9+ lowercase syntax

# Tuples - fixed-size, immutable
coordinates: Tuple[float, float] = (10.5, 20.3)
person: Tuple[str, int, bool] = ("Alice", 30, True)

# Variable-length tuples
numbers: Tuple[int, ...] = (1, 2, 3, 4, 5)  # Any number of ints

# Sets - unique elements
tags: Set[str] = {"python", "typing", "advanced"}

# Dictionaries
user_ages: Dict[str, int] = {"Alice": 30, "Bob": 25}
config: dict[str, str | int] = {"host": "localhost", "port": 8000}  # Python 3.10+
```

### Nested Collections
```python
# List of lists
matrix: List[List[int]] = [[1, 2], [3, 4]]

# Dict of lists
groups: Dict[str, List[str]] = {
    "admins": ["alice", "bob"],
    "users": ["charlie", "dave"]
}

# Complex nesting
data: Dict[str, List[Tuple[int, str]]] = {
    "results": [(1, "first"), (2, "second")]
}
```

### Sequence, Mapping, Iterable (Abstract Types)
```python
from typing import Sequence, Mapping, Iterable, Iterator

# Sequence - anything that supports indexing and len() (list, tuple, str)
def process_items(items: Sequence[int]) -> int:
    return sum(items)

process_items([1, 2, 3])      # OK
process_items((1, 2, 3))       # OK
process_items(range(1, 4))     # OK

# Mapping - read-only dict-like
def get_value(data: Mapping[str, int], key: str) -> int:
    return data[key]

# Iterable - anything you can loop over
def print_all(items: Iterable[str]) -> None:
    for item in items:
        print(item)

# Iterator - object returned by iter()
def count_items(iterator: Iterator[int]) -> int:
    return sum(1 for _ in iterator)
```

---

## 4. Optional and Union Types

### Optional (Union with None)
```python
from typing import Optional

# Optional[X] is shorthand for Union[X, None]
def find_user(user_id: int) -> Optional[str]:
    if user_id > 0:
        return f"User_{user_id}"
    return None

# Python 3.10+ syntax using | operator
def find_user(user_id: int) -> str | None:
    return None
```

### Union Types
```python
from typing import Union

# Multiple possible types
def process(value: Union[int, str]) -> str:
    if isinstance(value, int):
        return str(value)
    return value.upper()

# Python 3.10+ syntax
def process(value: int | str) -> str:
    return str(value)

# Multiple unions
Result = Union[int, str, float, None]

def compute() -> Result:
    return 42
```

### Type Guards for Union Narrowing
```python
def process(value: int | str) -> None:
    if isinstance(value, int):
        # Type checker knows value is int here
        print(value + 10)
    else:
        # Type checker knows value is str here
        print(value.upper())
```

---

## 5. Type Aliases

### Simple Aliases
```python
from typing import List, Dict, Tuple

# Create readable names for complex types
UserId = int
Username = str
UserData = Dict[str, str | int]

# Use in annotations
def get_user(user_id: UserId) -> Username:
    return f"user_{user_id}"

# Complex type aliases
Coordinate = Tuple[float, float]
Path = List[Coordinate]
RouteMap = Dict[str, Path]

route: RouteMap = {
    "route_a": [(0.0, 0.0), (1.0, 1.0)],
    "route_b": [(2.0, 2.0), (3.0, 3.0)]
}
```

### NewType (Distinct Types)
```python
from typing import NewType

# NewType creates a distinct type for type checking
UserId = NewType('UserId', int)
OrderId = NewType('OrderId', int)

def get_user(user_id: UserId) -> str:
    return f"User {user_id}"

def get_order(order_id: OrderId) -> str:
    return f"Order {order_id}"

# Creating instances
user_id = UserId(42)
order_id = OrderId(100)

get_user(user_id)    # OK
get_user(order_id)   # Type error! OrderId is not UserId
get_user(42)         # Type error! int is not UserId

# At runtime, UserId and OrderId are just int
print(user_id + 10)  # Works at runtime: 52
```

---

## 6. Callable Types

### Function Types
```python
from typing import Callable

# Callable[[arg_types], return_type]
def execute(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

def add(x: int, y: int) -> int:
    return x + y

result = execute(add, 5, 3)  # OK

# No arguments
Callback = Callable[[], None]

def run_callback(callback: Callback) -> None:
    callback()

# Variable arguments - use ...
Handler = Callable[..., None]

def register(handler: Handler) -> None:
    handler(1, 2, 3)  # Any args accepted
```

### Methods and Lambdas
```python
from typing import Callable

class Calculator:
    def add(self, x: int, y: int) -> int:
        return x + y

# Method type (self is not included)
Operation = Callable[[int, int], int]

calc = Calculator()
op: Operation = calc.add  # OK

# Lambdas
square: Callable[[int], int] = lambda x: x * x
```

---

## 7. Generic Types and TypeVar

### What Are Generics?
Generics allow you to write functions and classes that work with multiple types while maintaining type safety.

### Basic TypeVar
```python
from typing import TypeVar, List

# Define a type variable
T = TypeVar('T')

# Generic function - preserves input type
def first_item(items: List[T]) -> T:
    return items[0]

# Type checker infers:
x: int = first_item([1, 2, 3])        # T = int
y: str = first_item(["a", "b", "c"])  # T = str

# Multiple TypeVars
K = TypeVar('K')
V = TypeVar('V')

def get_first_pair(data: Dict[K, V]) -> Tuple[K, V]:
    key = next(iter(data.keys()))
    return key, data[key]
```

### Constrained TypeVar
```python
from typing import TypeVar

# Only allow specific types
NumberType = TypeVar('NumberType', int, float)

def double(value: NumberType) -> NumberType:
    return value * 2

double(5)      # OK - returns int
double(3.14)   # OK - returns float
double("hi")   # Type error!
```

### Bounded TypeVar
```python
from typing import TypeVar

# Must be a subclass of the bound
class Animal:
    def speak(self) -> str:
        return "..."

class Dog(Animal):
    def speak(self) -> str:
        return "Woof"

class Cat(Animal):
    def speak(self) -> str:
        return "Meow"

# T must be Animal or a subclass
T = TypeVar('T', bound=Animal)

def make_speak(animal: T) -> T:
    print(animal.speak())
    return animal

dog = Dog()
result: Dog = make_speak(dog)  # Returns Dog, not just Animal

# Type error - str is not bound by Animal
# make_speak("hello")
```

### Generic Classes
```python
from typing import Generic, TypeVar

T = TypeVar('T')

class Box(Generic[T]):
    def __init__(self, item: T) -> None:
        self.item = item
    
    def get(self) -> T:
        return self.item
    
    def set(self, item: T) -> None:
        self.item = item

# Usage
int_box: Box[int] = Box(42)
str_box: Box[str] = Box("hello")

x: int = int_box.get()        # OK
int_box.set(100)              # OK
int_box.set("wrong")          # Type error!

# Multiple type parameters
KT = TypeVar('KT')
VT = TypeVar('VT')

class Pair(Generic[KT, VT]):
    def __init__(self, key: KT, value: VT) -> None:
        self.key = key
        self.value = value

pair: Pair[str, int] = Pair("age", 30)
```

### Generic Functions with Bounds
```python
from typing import TypeVar, Protocol

class Comparable(Protocol):
    def __lt__(self, other: 'Comparable') -> bool: ...

T = TypeVar('T', bound=Comparable)

def find_min(items: List[T]) -> T:
    return min(items)

# Works with any comparable type
find_min([3, 1, 4, 1, 5])           # int
find_min([3.14, 2.71, 1.41])        # float
find_min(["zebra", "apple", "mango"])  # str
```

---

## 8. Protocol and Structural Subtyping

### What Are Protocols?
Protocols define interfaces based on structure (duck typing) rather than inheritance.

### Basic Protocol
```python
from typing import Protocol

class Drawable(Protocol):
    """Anything with a draw() method"""
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

class Square:
    def draw(self) -> None:
        print("Drawing square")

# Both Circle and Square implement Drawable without inheriting from it
def render(shape: Drawable) -> None:
    shape.draw()

render(Circle())  # OK
render(Square())  # OK
```

### Protocol with Attributes
```python
from typing import Protocol

class Named(Protocol):
    name: str

class Person:
    def __init__(self, name: str) -> None:
        self.name = name

class Product:
    def __init__(self, name: str, price: float) -> None:
        self.name = name
        self.price = price

def print_name(obj: Named) -> None:
    print(obj.name)

print_name(Person("Alice"))     # OK
print_name(Product("Book", 10)) # OK
```

### Generic Protocols
```python
from typing import Protocol, TypeVar

T = TypeVar('T')

class Container(Protocol[T]):
    def add(self, item: T) -> None: ...
    def get(self) -> T: ...

class IntContainer:
    def __init__(self) -> None:
        self._item: int = 0
    
    def add(self, item: int) -> None:
        self._item = item
    
    def get(self) -> int:
        return self._item

def process_container(container: Container[int]) -> int:
    container.add(42)
    return container.get()

process_container(IntContainer())  # OK
```

### Runtime Checkable Protocols
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...

class File:
    def close(self) -> None:
        print("Closing file")

# Can use isinstance at runtime
obj = File()
if isinstance(obj, Closeable):
    obj.close()
```

---

## 9. Literal Types

### Literal Values
```python
from typing import Literal

# Only specific values allowed
Mode = Literal["read", "write", "append"]

def open_file(filename: str, mode: Mode) -> None:
    print(f"Opening {filename} in {mode} mode")

open_file("data.txt", "read")    # OK
open_file("data.txt", "write")   # OK
open_file("data.txt", "delete")  # Type error!

# Literal with numbers
def set_priority(level: Literal[1, 2, 3]) -> None:
    print(f"Priority: {level}")

set_priority(1)  # OK
set_priority(4)  # Type error!

# Literal with booleans
def toggle(state: Literal[True]) -> None:  # Only True allowed
    pass
```

### Overloading with Literals
```python
from typing import Literal, overload

@overload
def fetch(key: Literal["user"]) -> str: ...

@overload
def fetch(key: Literal["age"]) -> int: ...

def fetch(key: Literal["user", "age"]) -> str | int:
    if key == "user":
        return "Alice"
    return 30

x: str = fetch("user")  # Type checker knows it returns str
y: int = fetch("age")   # Type checker knows it returns int
```

---

## 10. TypedDict

### What Is TypedDict?
TypedDict allows you to specify the structure of dictionaries with specific keys and value types.

### Basic TypedDict
```python
from typing import TypedDict

class Person(TypedDict):
    name: str
    age: int
    email: str

# Usage
person: Person = {
    "name": "Alice",
    "age": 30,
    "email": "alice@example.com"
}

# Type checking
print(person["name"])      # OK
print(person["age"] + 5)   # OK
print(person["missing"])   # Type error!
person["age"] = "thirty"   # Type error!
```

### Optional Keys
```python
from typing import TypedDict, NotRequired

# All keys required by default
class User(TypedDict):
    name: str
    age: int
    email: NotRequired[str]  # Python 3.11+ - this key is optional

user: User = {"name": "Bob", "age": 25}  # OK - email is optional

# Alternative syntax for older Python
class UserOld(TypedDict, total=False):
    email: str  # Optional

class UserOld2(TypedDict):
    name: str  # Required
    age: int   # Required
```

### Inheritance
```python
from typing import TypedDict

class BasePerson(TypedDict):
    name: str
    age: int

class Employee(BasePerson):
    employee_id: int
    department: str

emp: Employee = {
    "name": "Alice",
    "age": 30,
    "employee_id": 12345,
    "department": "Engineering"
}
```

### Alternative Syntax
```python
from typing import TypedDict

# Functional syntax (useful for keys that aren't valid identifiers)
Person = TypedDict('Person', {
    'name': str,
    'age': int,
    'user-id': int  # Hyphens not allowed in class syntax
})
```

---

## 11. Advanced Generic Patterns

### Variance (Covariance and Contravariance)
```python
from typing import TypeVar, Generic

# Covariant - preserves subtype relationship
T_co = TypeVar('T_co', covariant=True)

class Box(Generic[T_co]):
    def __init__(self, item: T_co) -> None:
        self._item = item
    
    def get(self) -> T_co:
        return self._item

class Animal: pass
class Dog(Animal): pass

dog_box: Box[Dog] = Box(Dog())
animal_box: Box[Animal] = dog_box  # OK - Box is covariant

# Contravariant - reverses subtype relationship
T_contra = TypeVar('T_contra', contravariant=True)

class Feeder(Generic[T_contra]):
    def feed(self, animal: T_contra) -> None:
        pass

animal_feeder: Feeder[Animal] = Feeder()
dog_feeder: Feeder[Dog] = animal_feeder  # OK - Feeder is contravariant
```

### ParamSpec for Callable Signatures
```python
from typing import TypeVar, Callable, ParamSpec

P = ParamSpec('P')
R = TypeVar('R')

# Preserves function signature
def log_call(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_call
def greet(name: str, age: int) -> str:
    return f"Hello {name}, age {age}"

# Type checker knows exact signature
result: str = greet("Alice", 30)  # OK
greet("Alice")                    # Type error - missing age
```

### Concatenate for Adding Parameters
```python
from typing import Callable, Concatenate, ParamSpec

P = ParamSpec('P')

class Request: pass

def with_request(
    func: Callable[Concatenate[Request, P], str]
) -> Callable[P, str]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> str:
        request = Request()
        return func(request, *args, **kwargs)
    return wrapper

@with_request
def handler(request: Request, user_id: int) -> str:
    return f"Handling request for user {user_id}"

# Type checker knows signature is just (user_id: int) -> str
result = handler(42)  # OK
```

---

## 12. Type Narrowing

### isinstance() Checks
```python
def process(value: int | str) -> None:
    if isinstance(value, int):
        # value is int here
        print(value + 10)
    else:
        # value is str here
        print(value.upper())
```

### None Checks
```python
def greet(name: str | None) -> str:
    if name is None:
        return "Hello, stranger"
    # name is str here (not None)
    return f"Hello, {name.upper()}"
```

### assert for Type Narrowing
```python
def process(value: int | None) -> int:
    assert value is not None  # Narrow type
    return value + 10  # OK - value is int
```

### Type Guards
```python
from typing import TypeGuard

def is_str_list(val: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)

def process(items: list[object]) -> None:
    if is_str_list(items):
        # items is list[str] here
        for item in items:
            print(item.upper())
```

### Custom Type Guards
```python
from typing import TypeGuard, TypeVar

T = TypeVar('T')

def is_not_none(val: T | None) -> TypeGuard[T]:
    return val is not None

def process(value: int | None) -> None:
    if is_not_none(value):
        # value is int here
        print(value + 10)
```

---

## 13. Escape Hatches and Workarounds

### 1. Any - Complete Opt-Out
```python
from typing import Any

# Any disables type checking
data: Any = {"key": "value"}
data.nonexistent_method()  # No error from type checker
result: int = data         # No error

# Use cases:
# - Working with truly dynamic data (JSON, user input)
# - Interfacing with untyped code
# - Prototyping
```

### 2. cast() - Explicit Type Assertion
```python
from typing import cast

# Tell type checker to trust you
result = some_untyped_function()
typed_result = cast(str, result)  # "I know this is str"

# Common use case: narrow types from Any
data: Any = {"name": "Alice", "age": 30}
user_dict = cast(dict[str, str | int], data)

# WARNING: cast() is a lie at runtime - doesn't validate!
x = cast(int, "hello")  # No runtime error, but will fail when used
```

### 3. type: ignore Comments
```python
# Suppress all errors on this line
result = problematic_code()  # type: ignore

# Suppress specific error codes (RECOMMENDED)
obj.unknown_attr  # type: ignore[attr-defined]
func(wrong_arg)   # type: ignore[arg-type]

# Common error codes:
# - attr-defined: Unknown attribute
# - arg-type: Wrong argument type
# - assignment: Invalid assignment
# - return-value: Wrong return type
# - import: Import error
# - union-attr: Attribute on union
# - call-arg: Wrong number of args
# - misc: Miscellaneous error
```

### 4. TYPE_CHECKING - Import Only for Checkers
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Only imported during type checking, not at runtime
    from expensive_module import HugeClass

def process(obj: "HugeClass") -> None:  # String annotation
    pass

# Solves circular imports:
# file_a.py
if TYPE_CHECKING:
    from file_b import ClassB

class ClassA:
    def method(self) -> "ClassB":
        from file_b import ClassB  # Import at runtime
        return ClassB()
```

### 5. @no_type_check Decorator
```python
from typing import no_type_check

@no_type_check
def untyped_function(x, y):
    # Type checker ignores entire function
    return x + y

@no_type_check
class UntypedClass:
    # Type checker ignores entire class
    def method(self, x):
        return x.whatever()
```

### 6. reveal_type() - Debugging Helper
```python
from typing import reveal_type

x = [1, 2, 3]
reveal_type(x)  # Type checker prints: Revealed type is 'list[int]'

def process(value: int | str) -> None:
    if isinstance(value, int):
        reveal_type(value)  # Revealed type is 'int'
    else:
        reveal_type(value)  # Revealed type is 'str'
```

### 7. Stub Files (.pyi)
```python
# mymodule.pyi - stub file with type information
def process_data(data: str) -> int: ...

class MyClass:
    def method(self, x: int) -> str: ...

# mymodule.py - actual implementation (can be untyped)
def process_data(data):
    return len(data)

class MyClass:
    def method(self, x):
        return str(x)
```

### 8. assert_type() - Runtime Type Validation
```python
from typing import assert_type

x: int = 42
assert_type(x, int)  # OK

y: str | int = "hello"
assert_type(y, str)  # Type error if y could be int
```

### 9. Generic Aliasing with TypeAlias
```python
from typing import TypeAlias

# Explicit type alias annotation (Python 3.10+)
UserId: TypeAlias = int
UserMap: TypeAlias = dict[UserId, str]

# Prevents confusion with regular assignments
x: TypeAlias = list[int]  # This is a type alias
y = list[int]             # This is a generic alias (different semantics)
```

### 10. Postponed Evaluation (from __future__)
```python
from __future__ import annotations

# All annotations become strings automatically
class Node:
    def __init__(self, value: int, next: Node | None = None):
        # Can reference Node before it's fully defined
        self.value = value
        self.next = next

# No need for quotes around forward references
def create_node() -> Node:
    return Node(1)
```

---

## 14. Best Practices

### 1. Start Simple, Add Complexity Gradually
```python
# Start with basic types
def add(a: int, b: int) -> int:
    return a + b

# Add generics when needed
from typing import TypeVar

T = TypeVar('T')

def add_generic(a: T, b: T) -> T:
    return a + b  # type: ignore[return-value]
```

### 2. Use Protocols Over Abstract Base Classes
```python
# ❌ Rigid inheritance
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self) -> str: ...

# ✅ Flexible structural typing
from typing import Protocol

class Speakable(Protocol):
    def speak(self) -> str: ...

# Any class with speak() method works
```

### 3. Prefer Specific Types Over Any
```python
# ❌ Too permissive
def process(data: Any) -> Any:
    return data

# ✅ More specific
def process(data: dict[str, int]) -> int:
    return sum(data.values())
```

### 4. Use Union Instead of Overly Generic Types
```python
# ❌ Too vague
def handle(value: object) -> None:
    pass

# ✅ Explicit possibilities
def handle(value: int | str | None) -> None:
    if isinstance(value, int):
        # Handle int
        pass
```

### 5. Annotate Public APIs, Consider Internal Code
```python
# Public API - always annotate
def calculate_total(prices: list[float]) -> float:
    return sum(prices)

# Internal helper - optional but helpful
def _validate_price(price: float) -> bool:
    return price > 0
```

### 6. Use NewType for Domain Types
```python
from typing import NewType

# Create distinct types for domain concepts
UserId = NewType('UserId', int)
ProductId = NewType('ProductId', int)

def get_user(user_id: UserId) -> str: ...
def get_product(product_id: ProductId) -> str: ...

# Prevents mixing up IDs
user_id = UserId(42)
product_id = ProductId(100)

get_user(user_id)      # OK
get_user(product_id)   # Type error!
```

### 7. Document Complex Type Aliases
```python
from typing import TypeAlias

# Good - clear documentation
JsonValue: TypeAlias = str | int | float | bool | None | dict[str, 'JsonValue'] | list['JsonValue']
"""A value that can be represented in JSON"""

# Use in annotations
def parse_json(data: str) -> JsonValue:
    import json
    return json.loads(data)
```

### 8. Use Literal for Enumerations
```python
from typing import Literal

# Better than string for fixed choices
Status = Literal["pending", "approved", "rejected"]

def update_status(status: Status) -> None:
    print(f"Status: {status}")

update_status("pending")    # OK
update_status("invalid")    # Type error!
```

### 9. Avoid Mutable Default Arguments
```python
# ❌ Mutable default
def append_to_list(item: int, lst: list[int] = []) -> list[int]:
    lst.append(item)
    return lst

# ✅ Use None as default
def append_to_list(item: int, lst: list[int] | None = None) -> list[int]:
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

### 10. Type Your Tests
```python
import pytest
from typing import Generator

@pytest.fixture
def sample_data() -> dict[str, int]:
    return {"a": 1, "b": 2}

def test_process(sample_data: dict[str, int]) -> None:
    result = process(sample_data)
    assert result == 3
```

### 11. Use Pyright/Mypy Configuration
```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
strict = true

[tool.pyright]
pythonVersion = "3.11"
typeCheckingMode = "strict"
reportMissingTypeStubs = false
```

### 12. Type Your Decorators
```python
from typing import TypeVar, Callable, ParamSpec

P = ParamSpec('P')
R = TypeVar('R')

def my_decorator(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name: str) -> str:
    return f"Hello, {name}"

# Type preserved through decorator
result: str = greet("Alice")  # OK
```

---

## Summary

### Key Takeaways

1. **Type hints are documentation and validation** - They don't affect runtime
2. **Start simple** - Add `int`, `str`, `list[int]` first
3. **Use generics for reusable code** - `TypeVar` for flexibility
4. **Protocols over inheritance** - Structural typing is more flexible
5. **Union for alternatives** - `int | str | None`
6. **Literal for constants** - `Literal["red", "green", "blue"]`
7. **TypedDict for structured dicts** - Better than `dict[str, Any]`
8. **Escape hatches exist** - Use `type: ignore[code]` sparingly
9. **Type checkers help** - Run mypy/pyright in CI/CD
10. **Read PEPs** - PEP 484, 526, 544, 585, 604, 612, 613, 646, 647, 673, 675, 681

### Further Reading
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [Pyright documentation](https://github.com/microsoft/pyright)
- [typing module documentation](https://docs.python.org/3/library/typing.html)
