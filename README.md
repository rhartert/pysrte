# Python bindings for SRTE-LS

This repository contains Python bindings for the [SRTE-LS] solver, which is 
implemented in Go. These bindings allow you to use the SRTE-LS solver in your 
Python projects.

## Usage

### Generating the Shared Object

To use the bindings, first generate the shared object by running the following 
command from the root of this repository:

```bash
go build -buildmode=c-shared -o srte-c-bindings.so .
```

### Running the Example

Once the shared object is generated, you can run `example.py`, which will use 
the bindings to optimize one of the instances in the `data/` directory.

```bash
python3 example.py 
```

After running `example.py`, you should see the following output:

```
utilization (before): 2.32526156375
utilization (after):  0.7930807129166667
```

[SRTE-LS]: https://github.com/rhartert/srte-ls