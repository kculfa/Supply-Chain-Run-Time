# Supply-Chain-Run-Time
(Latest version that is currently running is in the 'Supply-Chain-Run-Time' under the username ge87jiz)
After cloning the repoistory, please `cd` into the repository folder that was downloaded. The folder should be called `Supply-Chain-Run-Time` if you do not change it.

**IMPORTANT: PLEASE MAKE SURE TO RUN THE FLASK SERVER BEFORE THE VISUALIZATION**

## How to run the flask server

1. After `cd` into the repository folder, `cd` into the `my_flask_app` folder
2. Execute `python3 -m venv venv`
3. Execute `source venv/bin/activate`
4. Execute `pip install -r requirements.txt`
5. Execute `flask run --host=:: --port=9998`

## How to run the visualization

The visualization requires NodeJS https://nodejs.org/en/download

1. After running the flask server, Open another terminal `cd` again into the repository folder then, Execute `cd ..`. then `cd supply-chain-visualization`
2. Execute `npm i`
3. In the machine as far as I recall `npm`, `npx`, and an `npm` package called `serve` was preinstalled so I didn't have to install it. If it is **NOT** preinstalled on your machine, Execute `npm install -g serve`. **(THE INSTALLATION REQUIRES SUDO / ADMIN PRIVELAGES.)**
4. After that is done, Execute `npm run build`
5. Execute `npx serve -s build`

The visualization is now available at https://lehre.bpm.in.tum.de/ports/3000/  (IF IT IS NOT AVAILABLE ON THIS LINK PLEASE CHANGE THE 3000 IN THE LINK TO WHATEVER REACT SAYS PORT RUNS ON, FOR EXAMPLE IF IT SAYS- Local:    http://localhost:5555 THEN IT WILL BE AVAILABLE ON https://lehre.bpm.in.tum.de/ports/5555/  THIS IS NOT NEEDED UNLESS THE PORT 3000 IS BEING USED)

The visualization displays the change of the prices of 10 SKUs.
