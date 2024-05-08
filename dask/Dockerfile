FROM public.ecr.aws/docker/library/python:3.9
ENV USER root

# -------------------------------------------------------------------------------------
# openssh
# -------------------------------------------------------------------------------------

RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt install -y iproute2 cmake openssh-server openssh-client  build-essential gfortran wget curl
RUN pip install supervisor awscli

RUN mkdir -p /var/run/sshd
ENV DEBIAN_FRONTEND noninteractive

ENV NOTVISIBLE "in users profile"

#####################################################
## SSH SETUP

RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
RUN echo "export VISIBLE=now" >> /etc/profile

RUN echo "${USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
ENV SSHDIR /root/.ssh
RUN mkdir -p ${SSHDIR}
RUN touch ${SSHDIR}/sshd_config
RUN ssh-keygen -t rsa -f ${SSHDIR}/ssh_host_rsa_key -N ''
RUN cp ${SSHDIR}/ssh_host_rsa_key.pub ${SSHDIR}/authorized_keys
RUN cp ${SSHDIR}/ssh_host_rsa_key ${SSHDIR}/id_rsa
RUN echo " IdentityFile ${SSHDIR}/id_rsa" >> /etc/ssh/ssh_config
RUN echo "Host *" >> /etc/ssh/ssh_config && echo " StrictHostKeyChecking no" >> /etc/ssh/ssh_config
RUN chmod -R 600 ${SSHDIR}/* && \
chown -R ${USER}:${USER} ${SSHDIR}/
# check if ssh agent is running or not, if not, run
RUN eval `ssh-agent -s` && ssh-add ${SSHDIR}/id_rsa

##################################################


###################################################
## supervisor container startup

ADD conf/supervisord/supervisord.conf /etc/supervisor/supervisord.conf

EXPOSE 22
ADD batch-runtime-scripts/entry-point.sh batch-runtime-scripts/entry-point.sh
RUN chmod 0755 batch-runtime-scripts/entry-point.sh
ADD main.py main.py
CMD /batch-runtime-scripts/entry-point.sh