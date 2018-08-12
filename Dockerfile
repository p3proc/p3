# p3 docker image
FROM python:3.6.6-slim-stretch
MAINTAINER Andrew Van <vanandrew@wustl.edu>

# Install wget and curl
RUN apt-get update && \
    apt-get install -y wget curl

# Get afni
WORKDIR /
RUN apt-get install -y tcsh xfonts-base gsl-bin netpbm libjpeg62 xvfb xterm libxm4 build-essential libglw1-mesa && \
    mkdir afni && \
    cd /afni && \
    curl -O https://afni.nimh.nih.gov/pub/dist/tgz/linux_ubuntu_16_64.tgz && \
    tar -xvzf linux_ubuntu_16_64.tgz && \
    rm linux_ubuntu_16_64.tgz
ENV PATH=${PATH}:/afni/linux_ubuntu_16_64

# Compile and install fsl from source
# NOTE: I disable mist-clean because it doesn't compile for whatever reason...
# I add -std=c++03 to the compile flags because fsl assumes using a really old compiler... (SERIOUSLY UPDATE YOUR STUFF!!!)
WORKDIR /opt
ENV FSLDIR=/opt/fsl
RUN curl -O https://fsl.fmrib.ox.ac.uk/fsldownloads/fsl-5.0.10-sources.tar.gz && \
	tar zxf fsl-5.0.10-sources.tar.gz && \
	rm fsl-5.0.10-sources.tar.gz && \
    apt-get install -y libexpat1-dev libx11-dev libgl1-mesa-dev libglu1-mesa-dev zlib1g-dev dc bc && \
    sed -i '52iFSLCONFDIR=$FSLDIR/config' ${FSLDIR}/etc/fslconf/fsl.sh && \
	sed -i '53iFSLMACHTYPE=`$FSLDIR/etc/fslconf/fslmachtype.sh`' ${FSLDIR}/etc/fslconf/fsl.sh && \
	sed -i '57iexport FSLCONFDIR FSLMACHTYPE' ${FSLDIR}/etc/fslconf/fsl.sh && \
	sed -i "13s/ mist-clean\";/\";/" ${FSLDIR}/build && \
    . ${FSLDIR}/etc/fslconf/fsl.sh && \
	cp -r ${FSLDIR}/config/linux_64-gcc4.8 ${FSLDIR}/config/${FSLMACHTYPE} && \
    sed -i '22s/c++/c++ -std=c++03/' ${FSLDIR}/config/${FSLMACHTYPE}/systemvars.mk && \
	sed -i "3s/LIBXMLXX_CFLAGS=\"/LIBXMLXX_CFLAGS=\"-std=c++03 /" ${FSLDIR}/extras/src/libxml++-2.34.0/fslconfigure && \
    cd ${FSLDIR} && ./build && \
    rm -r ${FSLDIR}/LICENCE ${FSLDIR}/README ${FSLDIR}/build ${FSLDIR}/build.log ${FSLDIR}/config ${FSLDIR}/extras ${FSLDIR}/include ${FSLDIR}/lib ${FSLDIR}/refdoc ${FSLDIR}/src
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
ENV POSSUMDIR=${FSLDIR} OS=Linux FS_OVERRIDE=0 SUBJECTS_DIR=/opt/freesurfer/subjects FSF_OUTPUT_FORMAT=nii.gz \
    MNI_DIR=/opt/freesurfer/mni LOCAL_DIR=/opt/freesurfer/local FREESURFER_HOME=/opt/freesurfer \
    FSFAST_HOME=/opt/freesurfer/fsfast MINC_BIN_DIR=/opt/freesurfer/mni/bin \
    MINC_LIB_DIR=/opt/freesurfer/mni/lib MNI_DATAPATH=/opt/freesurfer/mni/data \
    FMRI_ANALYSIS_DIR=/opt/freesurfer/fsfast PERL5LIB=/opt/freesurfer/mni/lib/perl5/5.8.5 \
    MNI_PERL5LIB=/opt/freesurfer/mni/lib/perl5/5.8.5 \
    PATH=${PATH}:/opt/freesurfer/bin:/opt/freesurfer/fsfast/bin:/opt/freesurfer/tktools:/opt/freesurfer/mni/bin

# Install ANTS
WORKDIR /
RUN curl -O https://cmake.org/files/v3.12/cmake-3.12.0.tar.gz && \
    tar xvf cmake-3.12.0.tar.gz && rm cmake-3.12.0.tar.gz && \
    apt-get install -y git && \
    cd cmake-3.12.0 && ./bootstrap && make && make install && cd .. && rm -r cmake-3.12.0 && \
    git clone https://github.com/ANTsX/ANTs.git /ANTs-source && \
    mkdir ANTs && cd ANTs && cmake ../ANTs-source && make -j 6 && \
    cp -r ../ANTs-source/Scripts ./ && cd .. && rm -r ANTs-source
ENV ANTSPATH=/ANTs/bin
ENV PATH=${PATH}:${ANTSPATH}:/ANTs/Scripts

### MOVE ALL OF THIS ABOVE TO ANOTHER BASE IMAGE; BUILD OFF THAT BASE IMAGE ## 

# Install p3proc + other dependencies
RUN pip install p3proc && apt-get update && apt-get install -y graphviz

# Install bids-validator
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
    apt-get install -y nodejs && npm install -g bids-validator

# Set entrypoint
ENTRYPOINT ["p3proc"]
