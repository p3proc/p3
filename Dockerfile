# p3 docker image
FROM python:3.6.6-slim-stretch
MAINTAINER Andrew Van <vanandrew@wustl.edu>

# Install wget and curl
RUN apt-get update && \
    apt-get install -y wget curl

# Install stuff from neurodebian: fsleyes (I used to do afni, but it does weird stuff to template file locations...)
# I use the -allow-unauthenticated tag bc neurodebian needs to update their gpg keys!!!
# NOTE: I remove the neurodebian source afterwards since I don't verify it
RUN wget -O- http://neuro.debian.net/lists/stretch.us-ca.full | tee /etc/apt/sources.list.d/neurodebian.sources.list && \
    apt-get update && \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get install -yq --allow-unauthenticated fsleyes && \
    ln -s $(which FSLeyes) /usr/bin/fsleyes && \
    rm /etc/apt/sources.list.d/neurodebian.sources.list

# Get afni
WORKDIR /
RUN apt-get install -y tcsh xfonts-base gsl-bin netpbm libjpeg62 xvfb xterm libxm4 build-essential \
    mkdir afni && \
    cd /afni && \
    curl -O https://afni.nimh.nih.gov/pub/dist/tgz/linux_ubuntu_16_64.tgz && \
    tar -xvzf linux_ubuntu_16_64.tgz && \
    rm linux_ubuntu_16_64.tgz
ENV PATH=${PATH}:/afni/bin/linux_ubuntu_16_64

# Compile and install fsl from source
# NOTE: I disable mist-clean because it doesn't compile for whatever reason...
# I add -std=c++03 to the compile flags because fsl assumes using a really old compiler... (SERIOUSLY UPDATE YOUR STUFF!!!)
WORKDIR /opt
ENV FSLDIR=/opt/fsl
RUN curl -O https://fsl.fmrib.ox.ac.uk/fsldownloads/fsl-5.0.10-sources.tar.gz && \
	tar zxf fsl-5.0.10-sources.tar.gz && \
	rm fsl-5.0.10-sources.tar.gz && \
    apt-get install -y build-essential libexpat1-dev libx11-dev libgl1-mesa-dev libglu1-mesa-dev zlib1g-dev && \
    sed -i '52iFSLCONFDIR=$FSLDIR/config' ${FSLDIR}/etc/fslconf/fsl.sh && \
	sed -i '53iFSLMACHTYPE=`$FSLDIR/etc/fslconf/fslmachtype.sh`' ${FSLDIR}/etc/fslconf/fsl.sh && \
	sed -i '57iexport FSLCONFDIR FSLMACHTYPE' ${FSLDIR}/etc/fslconf/fsl.sh && \
	sed -i "13s/ mist-clean\";/\";/" ${FSLDIR}/build && \
    . ${FSLDIR}/etc/fslconf/fsl.sh && \
	cp -r ${FSLDIR}/config/linux_64-gcc4.8 ${FSLDIR}/config/${FSLMACHTYPE} && \
    sed -i '22s/c++/c++ -std=c++03/' ${FSLDIR}/config/${FSLMACHTYPE}/systemvars.mk && \
	sed -i "3s/LIBXMLXX_CFLAGS=\"/LIBXMLXX_CFLAGS=\"-std=c++03 /" ${FSLDIR}/extras/src/libxml++-2.34.0/fslconfigure && \
    cd ${FSLDIR} && ./build && \
    rm -r ${FSLDIR}/LICENCE ${FSLDIR}/README ${FSLDIR}/build ${FSLDIR}/build.log ${FSLDIR}/config ${FSLDIR}/extras ${FSLDIR}/include ${FSLDIR}/lib ${FSLDIR}/refdoc ${FSLDIR}/src && \
    apt-get remove -y build-essential && apt-get autoremove -y
ENV FSLOUTPUTTYPE=NIFTI_GZ FSLMULTIFILEQUIT=TRUE FSLTCLSH=${FSLDIR}/bin/fsltclsh FSLWISH=${FSLDIR}/fslwish PATH=${PATH}:${FSLDIR}/bin

# Install freesurfer and configure environment
RUN wget -qO- https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/6.0.1/freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.1.tar.gz | tar zxv --no-same-owner -C /opt \
    --exclude='freesurfer/trctrain' \
    --exclude='freesurfer/subjects/fsaverage_sym' \
    --exclude='freesurfer/subjects/fsaverage3' \
    --exclude='freesurfer/subjects/fsaverage4' \
    --exclude='freesurfer/subjects/fsaverage5' \
    --exclude='freesurfer/subjects/fsaverage6' \
    --exclude='freesurfer/subjects/cvs_avg35' \
    --exclude='freesurfer/subjects/cvs_avg35_inMNI152' \
    --exclude='freesurfer/subjects/bert' \
    --exclude='freesurfer/subjects/V1_average' \
    --exclude='freesurfer/average/mult-comp-cor' \
    --exclude='freesurfer/lib/cuda' \
    --exclude='freesurfer/lib/qt'
ENV POSSUMDIR=${FSLDIR}
ENV OS=Linux
ENV FS_OVERRIDE=0
ENV FIX_VERTEX_AREA=
ENV SUBJECTS_DIR=/opt/freesurfer/subjects
ENV FSF_OUTPUT_FORMAT=nii.gz
ENV MNI_DIR=/opt/freesurfer/mni
ENV LOCAL_DIR=/opt/freesurfer/local
ENV FREESURFER_HOME=/opt/freesurfer
ENV FSFAST_HOME=/opt/freesurfer/fsfast
ENV MINC_BIN_DIR=/opt/freesurfer/mni/bin
ENV MINC_LIB_DIR=/opt/freesurfer/mni/lib
ENV MNI_DATAPATH=/opt/freesurfer/mni/data
ENV FMRI_ANALYSIS_DIR=/opt/freesurfer/fsfast
ENV PERL5LIB=/opt/freesurfer/mni/lib/perl5/5.8.5
ENV MNI_PERL5LIB=/opt/freesurfer/mni/lib/perl5/5.8.5
ENV PATH=${PATH}:/opt/freesurfer/bin:/opt/freesurfer/fsfast/bin:/opt/freesurfer/tktools:/opt/freesurfer/mni/bin

# Install Python Stuff
WORKDIR /
ADD requirements.txt /
RUN pip install -r requirements.txt && \
    rm requirements.txt
