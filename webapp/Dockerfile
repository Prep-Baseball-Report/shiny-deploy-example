# Base image
FROM rocker/shiny-verse:4.2.2

ENV R_VERSION=4.2.2  

# system libraries of general use
## install debian packages
RUN apt-get update -qq && apt-get -y --no-install-recommends install \
    libxml2-dev \
    libcairo2-dev \
    libsqlite3-dev \
    libmariadbd-dev \
    libpq-dev \
    libssh2-1-dev \
    unixodbc-dev \
    libcurl4-openssl-dev \
    libssl-dev

## update system libraries
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean
   
# copy app folder and necessary files
COPY /app ./app

# install packages
RUN Rscript -e 'install.packages("shinyWidgets")' \
 && Rscript -e 'install.packages("shinydashboard")' \
 && Rscript -e 'install.packages("shinythemes")' \
 && Rscript -e 'install.packages("shinyjs")' \
 && Rscript -e 'install.packages("cowplot")' \
 && Rscript -e 'install.packages("gridExtra")' \
 && Rscript -e 'install.packages("kableExtra")' \
 && Rscript -e 'install.packages("formattable")' \
 && Rscript -e 'install.packages("plotly")' \
 && Rscript -e 'install.packages("DT")' \
 && Rscript -e 'install.packages("png")' \
 && Rscript -e 'install.packages("paws")' \
 && Rscript -e 'install.packages("aws.s3")' \
 && Rscript -e 'install.packages("animation")' \
 && Rscript -e 'install.packages("shinycssloaders")' \
 && Rscript -e 'install.packages("noctua")' 

# expose port
EXPOSE 3838

# run app on container start
CMD ["R", "-e", "shiny::runApp('/app', host = '0.0.0.0', port = 3838)"]


#docker commands
#docker build -t draft-league-app .
#docker run -e AWS_DEFAULT_REGION="%AWS_DEFAULT_REGION%" -e AWS_ACCESS_KEY_ID="%AWS_ACCESS_KEY_ID%" -e AWS_SECRET_ACCESS_KEY="%AWS_SECRET_ACCESS_KEY%" -p 3838:3838 draft-league-app 
