FROM public.ecr.aws/docker/library/python:3.9
ENV USER dask
COPY requirements.txt ./


RUN pip3 install -r requirements.txt

# -------------------------------------------------------------------------------------
# openssh
# -------------------------------------------------------------------------------------

RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt install -y iproute2 cmake openssh-server openssh-client  build-essential gfortran wget curl
RUN pip install supervisor awscli


RUN useradd -ms /bin/bash $USER
ENV HOME /home/$USER

#####################################################
## SSH SETUP
ENV SSHDIR $HOME/.ssh
RUN mkdir -p ${SSHDIR} \
 && touch ${SSHDIR}/sshd_config \
 && ssh-keygen -t rsa -f ${SSHDIR}/ssh_host_rsa_key -N '' \
 && cp ${SSHDIR}/ssh_host_rsa_key.pub ${SSHDIR}/authorized_keys \
 && cp ${SSHDIR}/ssh_host_rsa_key ${SSHDIR}/id_rsa \
 && echo "    IdentityFile ${SSHDIR}/id_rsa" >> ${SSHDIR}/config \
 && echo "    StrictHostKeyChecking no" >> ${SSHDIR}/config \
 && echo "    UserKnownHostsFile /dev/null" >> ${SSHDIR}/config \
 && echo "    Port 22" >> ${SSHDIR}/config \
 && echo 'Port 22' >> ${SSHDIR}/sshd_config \
 && echo 'UsePrivilegeSeparation no' >> ${SSHDIR}/sshd_config \
 && echo "HostKey ${SSHDIR}/ssh_host_rsa_key" >> ${SSHDIR}/sshd_config \
 && echo "PidFile ${SSHDIR}/sshd.pid" >> ${SSHDIR}/sshd_config \
 && chmod -R 600 ${SSHDIR}/* \
 && chown -R ${USER}:${USER} ${SSHDIR}/

# check if ssh agent is running or not, if not, run
RUN eval `ssh-agent -s` && ssh-add ${SSHDIR}/id_rsa
RUN chown ${USER}:${USER} -R /input

##################################################


###################################################
## supervisor container startup

ADD conf/supervisord/supervisord.conf /etc/supervisor/supervisord.conf

EXPOSE 22
ADD batch-runtime-scripts/entry-point.sh batch-runtime-scripts/entry-point.sh
RUN chmod 0755 batch-runtime-scripts/entry-point.sh
ADD main.py main.py
CMD /batch-runtime-scripts/entry-point.sh