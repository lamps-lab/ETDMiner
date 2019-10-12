FROM       tesseractshadow/tesseract4re

RUN        apt update && apt install -y ghostscript

WORKDIR    /app

COPY       runner.sh ./

RUN        chmod a+x runner.sh

ENTRYPOINT ["./runner.sh"]
