FROM python:3

ENV CHECKER_ADDRESS=
ENV CHECKER_PORT=
ENV CHECKER_DIRECTORIES=

WORKDIR /usr/src/app/

COPY free_space_checker.py  .

CMD python                     \
  ./free_space_checker.py      \
  --address ${CHECKER_ADDRESS} \
  --port ${CHECKER_PORT}       \
  --single-argument-dirs       \
  ${CHECKER_DIRECTORIES}
