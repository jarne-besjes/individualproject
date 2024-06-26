# Basic Complexity Analyser

## Functionality
All of the functionality is with C code
- See if loops terminate
- Check if recursive functions will terminate
- Calculate the WCET of loops
- Calculate the total WCET of a function
- Calculate the total WCET of a program

## Running the program
This should be as simple as running 
```bash
docker compose up --build
```
in the root directory.
Docker will make a `frontend` and `backend` container.
The `frontend` container is hosted at `http://localhost:3000`
The `backend` container is hosted at `http://localhost:8000`

When all images are started, you can access the program via the frontend.
Here you can enter your code and will see all the analytics on the code.
Note: Because this was more of a research project, the analyser supports only a small subset of the C language.



## Sources used
- Carl Österberg: Calculating of WCET with symbol execution, 08/2022 (accessed 24/6/2024)
  https://www.diva-portal.org/smash/get/diva2:1689116/FULLTEXT01.pdf

