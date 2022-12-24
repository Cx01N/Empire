FROM debian:buster
WORKDIR /empire
COPY . /empire
# No to all extras except yes to "Python 3.8"
RUN echo 'n\nn\nn\ny\n' | /empire/setup/install.sh
RUN rm -rf /empire/empire/server/data/empire*
RUN yes | ./ps-empire server --reset
ENTRYPOINT ["./ps-empire"]
CMD ["server"]
