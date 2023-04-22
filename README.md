# tSSP - Toy Supply-Side Platform 

The project represents SSP part of the RTB project made in collaboration with Armenian Code Academy students (python/django course).
It is based on the specification provided [here](https://github.com/0rps/aca_spec).

## Usage
The project could be started in two modes: dev/prod. But it could be improved since prod mode does not support grafana/prometheus and mongo-express.

### Dev mode
* SSP backend:
  * FastAPI server
  * Celery service
  * Mongo DB
  * Redis
* Mongo Express
* Frontend
* Prometheus + Grafana
* Test DSP

Could be started by the following commands:
```
docker-compose up --build frontend
docker-compose up --build grafana
docker-compose up --build dst.test
```

Open in browser: 
* http://127.0.0.1:4200 (RTB Game)
* http://127.0.0.1:7000 (Grafana) - login:password - admin:admin


### Prod mode
* SSP backend:
  * FastAPI server
  * Celery service
  * Mongo DB
  * Redis
* Nginx
* Test DSP

```
# If you want to change backend URL for frontend static then go to the ./frontend/src/enviroments/enviroment.ts and change appropriate URL.
cd frontend
npm ci && npm run build

cd ..
docker-compose up --build nginx
```

Default port for nginx: `14592`

The login/password is provided in `.resources/nginx/.htpasswd`.
Default login/password: `sspuser` and `test_password`.

### Test DSP 
The address of the test dsp: `http://dsp.test:8000`

## License

MIT License

Copyright (c) 2023

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.