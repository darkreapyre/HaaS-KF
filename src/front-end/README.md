# ML Workflow Front-end

## Deployment Notes
1. The following is a list of steps to reproduce [this](https://john.soban.ski/an-inexpensive-web-database-app-via-s3-part-one.html) in the context of the ML Workflow.
    - Ensure `virtualenv` is loaded (for the [Mac](https://sourabhbajaj.com/mac-setup/Python/virtualenv.html)).
    - Get the name of the S3 Bucket that was created by the ML Workflow "backend" and add it to `application.py`. For Example:
```bash
        S3_BUCKET=haas-dev-bucket-ussyc6snzrn0
        DASHBOARD_URL=http://127.0.0.1
```
    - Setup Python 3 virtual environment:
```bash
        cd src/front-end && \
        virtualenv -p python3 venv && \
        source ./venv/bin/activate
```
    - Install Python packages
```bash
        pip --no-cache-dir install -r requirements.txt

        deactivate
```
    - Create Package Manually
```bash
        cd venv/lib/python3.7/site-packages/

        zip -r9 ../../../../package.zip .

        cd ../../../../src/

        zip -rg ../package.zip *
```
2. In the case of the overall deployment of the MlOps workflow, the CloudFormation `package` command is used. However the appropriate `Python` libraries need to be installed. To do this, replace the previous step with the following:
```bash
    # Ensure cwd is set to `front-end`
    pip --no-cache-dir install -r requirements.txt -t src/

    deactivate
```

## Local Testing Notes
In order to test the solution locally before deployment, use the following steps:
1. Ensure `virtualenv` is loaded (for the [Mac](https://sourabhbajaj.com/mac-setup/Python/virtualenv.html)).
2. Get the name of the S3 Bucket that was created by the ML Workflow "backend" and add it to `application.py`. For Example:
```bash
    export S3_BUCKET=<S3 TEST Bucket>
    export DASHBOARD_URL=http://127.0.0.1
```
3. Setup Python 3 virtual environment:
```bash
    cd src/front-end && \
    virtualenv -p python3 venv && \
    source ./venv/bin/activate
```
4. Install Python packages:
```bash
    pip --no-cache-dir install -r requirements.txt
```
5. Run local Flask server:
```bash
    cd src
    
    python ./app.py
```
6. Open a web browser and navigate to `http://127.0.0.1:5000` to view the Front-End content.