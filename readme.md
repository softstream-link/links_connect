# Motivation
The library provides a number of utilities for working with implementations of [`links_bindings_python`](https://crates.io/crates/links_bindings_python) of the [`links`](https://github.com/softstream-link/links) `Rust` library. One such implementation example is a `pip`  [`ouch-connect`](https://pypi.org/project/ouch-connect) package.

# Included Facilities
## Callbacks
### Callbacks Utilities

  * [`links_connect.callbacks.Callback`](./src/links_connect/callbacks/_01_core/__init__.py#Callback) - a base class for implementing other callbacks, it provides abstract method signatures the following methods methods:
    * `def on_recv(self, con_id: ConId, msg: Message) -> None:`
    * `def on_sent(self, con_id: ConId, msg: Message) -> None:`
  * [`links_connect.callbacks.ChainableCallback`](./src/links_connect/callbacks/_02_chained/__init__.py#ChainableCallback) - a facility that is used as based for other callbacks and allows different types of callbacks to be chained and called in order.
    * Example:
      *  In this example the callback variable will perform both capture all messages in memory as well as log all messages using python's `logging` module
    ```python
    from links_connect.callbacks import LoggerCallback, MemoryStoreCallback
    callback = MemoryStoreCallback() + LoggerCallback()
    ```
  * [`links_connect.callbacks.DecoratorDriver`](./src/links_connect/callbacks/_04_decorator/driver.py#DecoratorDriver) - a base class for registering specific function calls when the `Message` matches the `Filter` using `@on_sent` & `@on_recv` decorators. Note that methods names can't override the `on_sent` & `on_recv` method names of the `links_connect.callbacks.Callback` base class.
    * Example:
    ```python
    from links_connect.callbacks import DecoratorDriver, on_sent, on_recv
    
    class MyCallback(DecoratorDriver):
        
        @on_sent(filter={})
        def on_sent_all(self, con_id: ConId, msg: Message) -> None:
            print(f"Sent: {msg}")

        @on_recv(filter={"LoginRequest": {}})
        def on_recv_login_request(self, con_id: ConId, msg: Message) -> None:
            print(f"Received: {msg}")
    ```

### Callback Implementations

  * [`links_connect.callbacks.LoggerCallback`](./src/links_connect/callbacks/_03_logger/__init__.py#LoggerCallback) - a callback that logs all messages `sent` & `received` at configured levels using python's `logging` module
  * [`links_connect.callbacks.MemoryStoreCallback`](./src/links_connect/callbacks/_05_store/__init__.py#MemoryStoreCallback) - captures all `sent` & `received` messages in memory and provides a number of `find` methods which accept `filters` & `connection id` for querying the captured messages
  

## Robot Framework Library
  * [`links_connect.runner.LinksRobotRunner`](./src/links_connect/runner/robotfwrk.py#LinksRobotRunner) - is a [`Robot Framework`](https://robotframework.org) library that enables end user in creation of test cases for `links` compatible python packages. 
  * See example of configuring a test suite & running it below.
    * [`variable.py`](./tests/links_connect/runner/robotfwrk/suites/ouch/variables.py) - this file contains `get_variables()` function that returns a dictionary of variables used by the `library` and the test cases.
    * [`login.robot`](./tests/links_connect/runner/robotfwrk/suites/ouch/login.robot) - this file initializes the `library` and performs a successful and fail login test using [`ouch-connect`](https://pypi.org/project/ouch-connect) package.