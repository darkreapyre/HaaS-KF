ARG MASTER_IMAGE
#ENV image=$(myapp:latest)
#RUN echo $MASTER_IMAGE
FROM $MASTER_IMAGE

ARG DASHBOARD_URL 
ENV DASHBOARD_URL=$DASHBOARD_URL

ARG NUM_GPUS
ENV NUM_GPUS=$NUM_GPUS

ARG DATASET_NAME
ENV DATASET_NAME=$DATASET_NAME

ARG EXPERIMENT_NAME
ENV EXPERIMENT_NAME=$EXPERIMENT_NAME


#FROM horovod:local

########################################################################################## 
# GitHub Training code
##########################################################################################  
COPY code /tmp/code 
RUN FILE=/tmp/code/setup.py && if [ -f "$FILE" ]; then cd /tmp/code; pip3 install .; fi
RUN FILE=/tmp/code/requirements.txt && if [ -f "$FILE " ]; then pip3 install -r $FILE; fi
RUN cp /tmp/code/train.py /train.py 

#ENTRYPOINT ["python3", "/launch.py"]