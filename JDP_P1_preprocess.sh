#!/bin/tcsh -xf

# $1 is the subject ID
# $2 is the parent directory

# have to load the FS module on Biowulf, need to establish paths
source $FREESURFER_HOME/SetUpFreeSurfer.csh

echo ----------------------------------------------------------
echo ----------------------------------------------------------
echo REMOVE OLD RESULTS COMPLETELY FOR SAFETY, OBTAIN RUNS
echo ----------------------------------------------------------
echo ----------------------------------------------------------

set sub = $1
set pdir = $2
set scriptdir = ${pdir}/scripts
set subdir = ${pdir}/subs/$sub
set resultsdir = ${subdir}/P1.results
set FSdir = ${pdir}/FSsurfaces/${sub}

# set up file system for PAPER1, copy in BOLD and MPRAGE files
cd $subdir
rm -rf ${resultsdir}
mkdir -p ${resultsdir}
cp *${sub}*nii.gz ${resultsdir}/
cp *${sub}*.TR ${resultsdir}/
cp *${sub}*.SLICETIME ${resultsdir}/
cp *${sub}*.SKIPTRS ${resultsdir}/
cp ${scriptdir}/TT_N27.nii.gz ${resultsdir}/
cd ${resultsdir}

# now that we're in resultsdir, which is newly created and populated
# change some filenames for ease of compatability across datasets
set mprname = (`ls *${sub}*prage*nii.gz`)
mv ${mprname} mprage.nii.gz


# use only sizeable BOLD runs with 100+ volumes
# also ensure we know the TR and slice time information as this is often wrong/missing in the header
# if the above happens, TSHIFT operations will be incorrect, so gotta be careful about this
set epiRunNames = (`ls *${sub}*est*nii.gz`)
echo $epiRunNames
set numRuns = $#epiRunNames
set runconvertfile = ${resultsdir}/runconvertfile.txt
rm -f ${runconvertfile}
touch ${runconvertfile}
set runs = ()
set trs = ()
set slicetimes = ()
set skiptrs = ()
@ runctr = 0
foreach runfile ( $epiRunNames )
@ runctr += 1
set nv = `3dinfo -nv ${runfile}`
if ($nv > 100) then
set runs = ($runs:q $runctr)
mv ${runfile} ${sub}_rest${runctr}.nii.gz
echo "${runfile} ${sub}_rest${runctr}.nii.gz" >> ${runconvertfile}

# here we check for TR and SLICETIME and SKIPTRS information and create arrays for TSHIFT to use in the future
set imgstem = `echo ${runfile} | sed 's/\(.*\)\.\(.*\)\.\(.*\)/\1/g'`
ls
if ( -f ${imgstem}.TR ) then
mv ${imgstem}.TR ${sub}_rest${runctr}.TR
else
echo ERROR ${imgstem}.TR does not exist
endif
if ( -f ${imgstem}.SLICETIME ) then
mv ${imgstem}.SLICETIME ${sub}_rest${runctr}.SLICETIME
else
echo ERROR ${imgstem}.SLICETIME does not exist
endif
if ( -f ${imgstem}.SKIPTRS ) then
mv ${imgstem}.SKIPTRS ${sub}_rest${runctr}.SKIPTRS
else
echo ERROR ${imgstem}.SKIPTRS does not exist
endif
set tmptr = `cat ${sub}_rest${runctr}.TR`
set trs = ($trs:q $tmptr)
set tmpslt = `cat ${sub}_rest${runctr}.SLICETIME`
set slicetimes = ($slicetimes:q $tmpslt)
set tmpskp = `cat ${sub}_rest${runctr}.SKIPTRS`
set skiptrs = ($skiptrs:q $tmpskp)

else
echo "${runfile} NOT USED" >> ${runconvertfile}
endif
end
set firstRun = $runs[1]
echo ${runs} > ${resultsdir}/runlist.txt
echo ${runs}
echo ${trs}
echo ${slicetimes}

# at this point the script should be entirely generic other than the ${pdir}
# whatever the MPRAGE was, it is now mprage.nii.gz
# whatever the BOLD was, it is now ${sub}_rest${run}.nii.gz where run are ascending integers


echo ----------------------------------------------------------
echo ----------------------------------------------------------
echo THE VARIOUS PROCESSING STRATEGIES FOR THE DESPIKE PAPER
echo ----------------------------------------------------------
echo ----------------------------------------------------------

# run loop 1
@ runctr = 0
foreach run ($runs)
@ runctr++
set runslicetime = ${slicetimes[${runctr}]}
# ignore the first X frames (TSHIFT, DESPIKE)
set ignorefr = ${skiptrs[${runctr}]}

# create a copy of the image
3dTcat \
-prefix pb01.${sub}.rest${run}.tcat.nii.gz \
${sub}_rest${run}.nii.gz'[0..$]'
# create the despike image
3dDespike \
-ignore ${ignorefr} \
-NEW \
-nomask \
-ssave pb02.${sub}.rest${run}.despike_SPIKES.nii.gz \
-prefix pb02.${sub}.rest${run}.despike.nii.gz \
pb01.${sub}.rest${run}.tcat.nii.gz

# create the despike+tshift image
if ( ${runslicetime} == 'nogo' ) then
echo WARNING No need to slice time correct or the slice timing is unspecified
cp pb02.${sub}.rest${run}.despike.nii.gz pb03.${sub}.rest${run}.despike.tshift.nii.gz
else
3dTshift \
-ignore ${ignorefr} \
-tzero 0 \
-tpattern ${runslicetime} \
-heptic \
-prefix pb03.${sub}.rest${run}.despike.tshift.nii.gz \
pb02.${sub}.rest${run}.despike.nii.gz
endif

# create the tshift image
if ( ${runslicetime} == 'nogo' ) then
echo WARNING No need to slice time correct or the slice timing is unspecified
cp pb01.${sub}.rest${run}.tcat.nii.gz pb04.${sub}.rest${run}.tshift.nii.gz
else
3dTshift \
-ignore ${ignorefr} \
-tzero 0 \
-tpattern ${runslicetime} \
-heptic \
-prefix pb04.${sub}.rest${run}.tshift.nii.gz \
pb01.${sub}.rest${run}.tcat.nii.gz
endif

# create the tshift+despike
3dDespike \
-ignore ${ignorefr} \
-NEW \
-nomask \
-ssave pb05.${sub}.rest${run}.tshift.despike_SPIKES.nii.gz \
-prefix pb05.${sub}.rest${run}.tshift.despike.nii.gz \
pb04.${sub}.rest${run}.tshift.nii.gz

# motion correct each of these files
set rawimgs = ( \
pb01.${sub}.rest${run}.tcat \
pb02.${sub}.rest${run}.despike \
pb03.${sub}.rest${run}.despike.tshift \
pb04.${sub}.rest${run}.tshift \
pb05.${sub}.rest${run}.tshift.despike \
)
foreach rawimg ( $rawimgs )
# register to the 1st used volume of the first run (volume 4 counting from zero of pb01.x.rest1.tcat)
3dvolreg \
-heptic \
-maxite 25 \
-verbose \
-zpad 10 \
-base pb01.${sub}.rest${firstRun}.tcat.nii.gz'[4]' \
-1Dfile ${rawimg}.motion_REF-EPI1.1D \
-1Dmatrix_save ${rawimg}.motion_REF-EPI1.aff12.1D \
-prefix ${rawimg}.motion_REF-EPI1.nii.gz \
${rawimg}.nii.gz

# register to the 1st used volume of the same run (volume 4 counting from zero of pb01.x.restX.tcat)
3dvolreg \
-heptic \
-maxite 25 \
-verbose \
-zpad 10 \
-base pb01.${sub}.rest${run}.tcat.nii.gz'[4]' \
-1Dfile ${rawimg}.motion_REF-INT.1D \
-1Dmatrix_save ${rawimg}.motion_REF-INT.aff12.1D \
-prefix jk.${rawimg}.motion_REF-INT.nii.gz \
${rawimg}.nii.gz
rm -f jk.*
end

# end run loop 1
end

echo ----------------------------------------------------------
echo ----------------------------------------------------------
echo SKULLSTRIP THE MPRAGE AND REGISTER IT TO THE ATLAS
echo ----------------------------------------------------------
echo ----------------------------------------------------------


# AFNI skull stripped images are missing edge of cortical ribbon often
# FSL has more of the ribbon often but can have weird neck stuff too
# Freesurfer rarely clips and is the most lenient of the skullstrips
3dSkullStrip -input mprage.nii.gz -prefix mprage.noskull_afni.nii.gz -orig_vol
bet mprage.nii.gz mprage.noskull_fslbet.nii.gz

# import Freesurfer skullstrip and transform it
# create transformation of FSorig to mprage.nii.gz
mri_convert ${FSdir}/mri/orig.mgz ./FSorig.nii.gz
mri_convert ${FSdir}/mri/brainmask.mgz ./FSbrainmask.nii.gz
3dAllineate \
-1Dmatrix_save FSorig.XFM.FS2MPR.aff12.1D \
-prefix FSorig_FS2MPR.nii.gz \
-base mprage.nii.gz \
-overwrite \
-input FSorig.nii.gz
3drefit -atrcopy mprage.noskull_afni.nii.gz IJK_TO_DICOM_REAL FSorig_FS2MPR.nii.gz
# create atlas-aligned version of skull stripped FS image
3dAllineate \
-1Dmatrix_apply FSorig.XFM.FS2MPR.aff12.1D \
-prefix mprage.noskull_FS.nii.gz \
-base mprage.nii.gz \
-input FSbrainmask.nii.gz \
-overwrite \
-nopad
3drefit -atrcopy mprage.noskull_afni.nii.gz IJK_TO_DICOM_REAL mprage.noskull_FS.nii.gz
# intensities are differently scaled in FS image, replace with native intensities for uniformity
3dcalc -a mprage.nii.gz -b mprage.noskull_FS.nii.gz  \
-expr 'a*and(b,b)' \
-overwrite \
-prefix mprage.noskull_FS.nii.gz
rm FSorig.nii.gz FSorig_FS2MPR.nii.gz FSbrainmask.nii.gz

# Use OR of AFNI, FSL, and FS skullstrips within a 3-shell expanded AFNI mask as final

3dcalc -a mprage.noskull_afni.nii.gz \
-expr 'step(a)' \
-overwrite \
-prefix jk.afmaskex0.nii.gz

3dcalc -a jk.afmaskex0.nii.gz -b a+i -c a-i -d a+j -e a-j -f a+k -g a-k  \
-expr 'ispositive(a+b+c+d+e+f+g)' \
-overwrite \
-prefix jk.afmaskex1.nii.gz

3dcalc -a jk.afmaskex1.nii.gz -b a+i -c a-i -d a+j -e a-j -f a+k -g a-k  \
-expr 'ispositive(a+b+c+d+e+f+g)' \
-overwrite \
-prefix jk.afmaskex2.nii.gz

3dcalc -a jk.afmaskex2.nii.gz -b a+i -c a-i -d a+j -e a-j -f a+k -g a-k  \
-expr 'ispositive(a+b+c+d+e+f+g)' \
-overwrite \
-prefix jk.afmaskex3.nii.gz

3dcalc -a jk.afmaskex3.nii.gz -b mprage.noskull_fslbet.nii.gz -c mprage.nii.gz -d mprage.noskull_afni.nii.gz \
-expr 'c*and(a,or(b,d))' \
-overwrite \
-prefix mprage.noskull_old.nii.gz

3dcalc -a jk.afmaskex3.nii.gz -b mprage.noskull_fslbet.nii.gz -c mprage.nii.gz -d mprage.noskull_afni.nii.gz -e mprage.noskull_FS.nii.gz  \
-expr 'c*and(a,or(b,d,e))' \
-overwrite \
-prefix mprage.noskull.nii.gz

rm jk.*.nii.gz

# register the skull-stripped MPRAGE to the TT_N27 atlas
@auto_tlrc -no_ss -base TT_N27+tlrc -input mprage.noskull.nii.gz -pad_input 60
# clean up
rm mprage.noskull_at.nii_WarpDrive.log
rm mprage.noskull_at.Xat.1D
gzip mprage.noskull_at.nii

# also transform the un-skull-stripped mprage
3dAllineate \
-input mprage.nii.gz \
-1Dmatrix_apply mprage.noskull_at.nii.Xaff12.1D \
-overwrite \
-prefix mprage_at.nii.gz \
-base TT_N27.nii.gz

# this transform is in the MPR->ATL direction: mprage.noskull_at.nii.Xaff12.1D
cp mprage.noskull_at.nii.Xaff12.1D mprage.XFM.MPR_to_ATL.Xaff12.1D



# for comparison, calculate the transform with only the AFNI version
@auto_tlrc -no_ss -base TT_N27+tlrc -input mprage.noskull_afni.nii.gz -pad_input 60
rm mprage.noskull_afni_at.nii_WarpDrive.log
rm mprage.noskull_afni_at.Xat.1D
gzip mprage.noskull_afni_at.nii

# also transform the un-skull-stripped mprage
3dAllineate \
-input mprage.nii.gz \
-1Dmatrix_apply mprage.noskull_afni_at.nii.Xaff12.1D \
-overwrite \
-prefix mprage_afni_at.nii.gz \
-base TT_N27.nii.gz


echo ----------------------------------------------------------
echo ----------------------------------------------------------
echo REGISTER THE BOLD DATA TO THE MPRAGE
echo ----------------------------------------------------------
echo ----------------------------------------------------------

# run loop 1
foreach run ($runs)

# use a single volume as the bridge to the mprage
# would be better to use an average over a motion-corrected scan, but that will interact with all the things I'm studying
set REGVOLNUM = 4
set EPIREF = pb01.${sub}.rest${run}.tcat${REGVOLNUM}
3dTcat -prefix ${EPIREF}.nii.gz pb01.${sub}.rest${run}.tcat.nii.gz'['${REGVOLNUM}']'

# skull strip the EPI
#AFNI skullstrip is too aggressive, use BET and automask instead
bet ${EPIREF}.nii.gz ${EPIREF}.noskull_fslbet.nii.gz
3dAutomask -overwrite -apply_prefix ${EPIREF}.noskull_afni.nii.gz ${EPIREF}.nii.gz
3dcalc -a ${EPIREF}.noskull_afni.nii.gz -b ${EPIREF}.noskull_fslbet.nii.gz -c ${EPIREF}.nii.gz \
-expr 'c*or(a,b)' \
-overwrite \
-prefix ${EPIREF}.noskull.nii.gz

# deoblique the MPRAGE and compute the transform between EPIREF and MPRAGE obliquity
3dWarp \
-verb \
-card2oblique ${EPIREF}.noskull.nii.gz \
-prefix jk.mprage.noskull_ob \
-newgrid 1.000000 \
-overwrite \
mprage.noskull.nii.gz \
| grep -A 4 '# mat44 Obliquity Transformation ::' > ${EPIREF}.mprage.noskull_obla2e_mat.1D

# resample the EPIREF to the MPRAGE
3dresample \
-master jk.mprage.noskull_ob+orig \
-prefix jk.${EPIREF}.noskull_rs \
-inset ${EPIREF}.noskull.nii.gz \
-rmode Cu

# calculate a weight mask for the lpc weighting
set perc = `3dBrickStat -automask -percentile 90.000000 1 90.000000  ${EPIREF}.noskull.nii.gz | tail -n1 | awk '{print $2}' `
3dcalc \
-datum float \
-prefix jk.${EPIREF}.noskull_rs_wt \
-a jk.${EPIREF}.noskull_rs+orig \
-expr 'min(1,(a/'${perc}'))'

# register the mprage to the tcat (BASE=TARGET, REGISTER TO THIS SPACE; SOURCE=INPUT, LEAVE THIS SPACE)
# this registration is on images with the same grids, whose obliquity has been accounted for
# hence the e2a_only designation of the affine matrix
3dAllineate \
-lpc \
-wtprefix jk.mprage.noskull_ob_wtal \
-weight jk.${EPIREF}.noskull_rs_wt+orig \
-source jk.mprage.noskull_ob+orig \
-prefix jk.mprage.noskull_ob_at \
-base jk.${EPIREF}.noskull_rs+orig \
-nocmass \
-1Dmatrix_save ${EPIREF}.mprage.noskull_e2a_only_mat.aff12.1D \
-master SOURCE \
-weight_frac 1.0 \
-maxrot 6 \
-maxshf 10 \
-VERB \
-warp aff \
-source_automask+4 \
-twopass \
-twobest 11

# TRANSFORM rawEPI into ATL space
# concatenate MPR-ATL -I, OBMPR-OBEPI, and MPR-EPI -I into a master transform
cat_matvec -ONELINE \
mprage.noskull_at.nii.gz::WARP_DATA -I \
${EPIREF}.mprage.noskull_obla2e_mat.1D \
${EPIREF}.mprage.noskull_e2a_only_mat.aff12.1D -I \
> ${EPIREF}.XFM.rawEPI_to_ATL.aff12.1D

# transform the tcat image into the atlas space via the mprage transform
3dAllineate \
-base mprage.noskull_at.nii.gz \
-1Dmatrix_apply ${EPIREF}.XFM.rawEPI_to_ATL.aff12.1D \
-prefix ${EPIREF}.noskull_at.nii.gz \
-input ${EPIREF}.noskull.nii.gz \
-verb \
-master BASE \
-mast_dxyz 3 \

# TRANSFORM rawEPI into MPR space
cat_matvec -ONELINE \
${EPIREF}.mprage.noskull_obla2e_mat.1D \
${EPIREF}.mprage.noskull_e2a_only_mat.aff12.1D -I \
> ${EPIREF}.XFM.rawEPI_to_MPR.aff12.1D

# transform the tcat image into the atlas space via the mprage transform
3dAllineate \
-base mprage.noskull.nii.gz \
-1Dmatrix_apply ${EPIREF}.XFM.rawEPI_to_MPR.aff12.1D \
-prefix ${EPIREF}.noskull_MPR.nii.gz \
-input ${EPIREF}.noskull.nii.gz \
-verb \
-master BASE \
-overwrite
# if the mprage is oblique (it probably is) you have to manually restore the obliquity
# becaue 3dAllineate (and many AFNI tools) set the image to Plumb even if it isn't
3drefit -atrcopy mprage.noskull.nii.gz IJK_TO_DICOM_REAL ${EPIREF}.noskull_MPR.nii.gz

rm jk.*

# end run loop
end


echo ----------------------------------------------------------
echo ----------------------------------------------------------
echo REGISTER BOLD RUNS TO EACH OTHER IF MULTIPLE RUNS
echo ----------------------------------------------------------
echo ----------------------------------------------------------

# you have to do cross-run alignment for anatomical consistency across runs
# 3dvolreg can do this for you, or you can do it yourself. this is the yourself version.
# here we register the reference images from each run to the first run reference
# NOTE: MI and NMI seem to do a better intra-modal job of registering than correlation-based methods

@ runctr = 0
foreach run ($runs)
@ runctr += 1

if ( $runctr == 1 ) then
set MASTEREPIREF = pb01.${sub}.rest${run}.tcat${REGVOLNUM}
set EPIREF = pb01.${sub}.rest${run}.tcat${REGVOLNUM}
else
set EPIREF = pb01.${sub}.rest${run}.tcat${REGVOLNUM}

# deoblique the MASTEREPIREF and compute the transform between EPIREF and MASTEREPIREF obliquity
3dWarp \
-verb \
-card2oblique ${EPIREF}.nii.gz \
-prefix jk.masterepi_ob \
-overwrite \
${MASTEREPIREF}.nii.gz \
| grep -A 4 '# mat44 Obliquity Transformation ::' > ${EPIREF}_EPI1_obla2e_mat.1D

# resample the EPIREF to the MASTEREPIREF grid
3dresample \
-master jk.masterepi_ob+orig \
-prefix jk.epi_rs \
-inset ${EPIREF}.nii.gz \
-rmode Cu

# register the MASTER to the EPIREF
3dAllineate \
-source jk.masterepi_ob+orig \
-prefix jk.masterepi_ob_to_EPI1 \
-base jk.epi_rs+orig \
-nocmass \
-1Dmatrix_save ${EPIREF}_EPI1_e2a_only_mat.aff12.1D \
-master SOURCE \
-VERB \
-warp shift_rotate \
-source_automask \
-twopass \
-twobest 11 \
-autoweight \
-cost nmi

rm jk*


# TRANSFORM rawEPI into ATL space
# concatenate MPR-ATL -I, OBMPR-OBEPI, and MPR-EPI -I into a master transform
cat_matvec -ONELINE \
mprage.noskull_at.nii.gz::WARP_DATA -I \
${MASTEREPIREF}.mprage.noskull_obla2e_mat.1D \
${MASTEREPIREF}.mprage.noskull_e2a_only_mat.aff12.1D -I \
${EPIREF}_EPI1_obla2e_mat.1D \
${EPIREF}_EPI1_e2a_only_mat.aff12.1D -I \
> ${EPIREF}.XFM.rawEPI_viaEPI1_to_ATL.aff12.1D

# transform the tcat image into the atlas space via the mprage-EPI1 transform
3dAllineate \
-base mprage.noskull_at.nii.gz \
-1Dmatrix_apply ${EPIREF}.XFM.rawEPI_viaEPI1_to_ATL.aff12.1D \
-prefix ${EPIREF}_viaEPI1_at.nii.gz \
-input ${EPIREF}.noskull.nii.gz \
-verb \
-master BASE \
-mast_dxyz 3 \
-overwrite \

# TRANSFORM rawEPI into EPI1 space
cat_matvec -ONELINE \
${EPIREF}_EPI1_obla2e_mat.1D \
${EPIREF}_EPI1_e2a_only_mat.aff12.1D -I \
> ${EPIREF}.XFM.rawEPI_to_EPI1.aff12.1D

# transform the tcat image into the EPI1 space
3dAllineate \
-base ${MASTEREPIREF}.nii.gz \
-1Dmatrix_apply ${EPIREF}.XFM.rawEPI_to_EPI1.aff12.1D \
-prefix ${EPIREF}_EPI1.nii.gz \
-input ${EPIREF}.noskull.nii.gz \
-verb \
-master BASE \
-overwrite
# if the mprage is oblique (it probably is) you have to manually restore the obliquity
# it would be nice if 3dAllineate didn't set this to Plumb by default
3drefit -atrcopy ${MASTEREPIREF}.nii.gz IJK_TO_DICOM_REAL ${EPIREF}_EPI1.nii.gz

endif

end





echo ----------------------------------------------------------
echo ----------------------------------------------------------
echo CREATE ATLAS-REGISTERED BOLD DATA
echo ----------------------------------------------------------
echo ----------------------------------------------------------

# loop runs
@ runctr = 0
foreach run ($runs)
@ runctr += 1
set runslicetime = ${slicetimes[${runctr}]}

set REGVOLNUM = 4
set EPIREF = pb01.${sub}.rest${run}.tcat${REGVOLNUM}

# loop images in runs
set rawimgs = ( \
pb01.${sub}.rest${run}.tcat \
pb02.${sub}.rest${run}.despike \
pb03.${sub}.rest${run}.despike.tshift \
pb04.${sub}.rest${run}.tshift \
pb05.${sub}.rest${run}.tshift.despike \
)
foreach img ( ${rawimgs} )

# there are 3 ways to bring rawEPI into the ATLAS space (all need volreg, epi-mpr, and mpr-atl:
# use the volreg results with EPI1 as the referent, and the epi-mpr transform for EPI1
# use the volreg results with INT  as the referent, and the epi-mpr transform for EPI1
# use the volreg results with INT  as the referent, and the epi-mpr tranfrorm for EPIX
#
# only the first and second options will enforce cross-run alignment

if ( $runctr == 1 ) then
# for run 1, all methods are the same
cat_matvec -ONELINE \
mprage.noskull_at.nii.gz::WARP_DATA -I \
${MASTEREPIREF}.mprage.noskull_obla2e_mat.1D \
${MASTEREPIREF}.mprage.noskull_e2a_only_mat.aff12.1D -I \
${img}.motion_REF-EPI1.aff12.1D \
> ${img}.XFM.EPI2EPI2MPR2ATL.aff12.1D

3dAllineate \
-overwrite \
-base mprage.noskull_at.nii.gz \
-input ${img}.nii.gz \
-1Dmatrix_apply ${img}.XFM.EPI2EPI2MPR2ATL.aff12.1D \
-mast_dxyz 3 \
-prefix ${img}.atlas.nii.gz

# this is the afni-skullstrip comparison
cat_matvec -ONELINE \
mprage.noskull_afni_at.nii.gz::WARP_DATA -I \
${MASTEREPIREF}.mprage.noskull_obla2e_mat.1D \
${MASTEREPIREF}.mprage.noskull_e2a_only_mat.aff12.1D -I \
${img}.motion_REF-EPI1.aff12.1D \
> ${img}.XFM.EPI2EPI2MPR2ATL_afni.aff12.1D

3dAllineate \
-overwrite \
-base mprage.noskull_at.nii.gz \
-input ${img}.nii.gz \
-1Dmatrix_apply ${img}.XFM.EPI2EPI2MPR2ATL_afni.aff12.1D \
-mast_dxyz 3 \
-prefix ${img}.atlas_afni.nii.gz

else
# method 1
cat_matvec -ONELINE \
mprage.noskull_at.nii.gz::WARP_DATA -I \
${MASTEREPIREF}.mprage.noskull_obla2e_mat.1D \
${MASTEREPIREF}.mprage.noskull_e2a_only_mat.aff12.1D -I \
${img}.motion_REF-EPI1.aff12.1D \
> ${img}.XFM.EPI2EPI2MPR2ATL.aff12.1D

3dAllineate \
-overwrite \
-base mprage.noskull_at.nii.gz \
-input ${img}.nii.gz \
-1Dmatrix_apply ${img}.XFM.EPI2EPI2MPR2ATL.aff12.1D\
-mast_dxyz 3 \
-prefix ${img}.atlas.nii.gz

# check the other methods just using the raw data, not all images
if ( "$img" == "pb01.${sub}.rest${run}.tcat" ) then

# method 2
cat_matvec -ONELINE \
mprage.noskull_at.nii.gz::WARP_DATA -I \
${MASTEREPIREF}.mprage.noskull_obla2e_mat.1D \
${MASTEREPIREF}.mprage.noskull_e2a_only_mat.aff12.1D -I \
${EPIREF}_EPI1_obla2e_mat.1D \
${EPIREF}_EPI1_e2a_only_mat.aff12.1D -I \
${img}.motion_REF-INT.aff12.1D \
> ${img}.XFM.EPI2EPI2MPR2ATL_motionINT_EPIxEPI1.aff12.1D

3dAllineate \
-overwrite \
-base mprage.noskull_at.nii.gz \
-input ${img}.nii.gz \
-1Dmatrix_apply ${img}.XFM.EPI2EPI2MPR2ATL_motionINT_EPIxEPI1.aff12.1D \
-mast_dxyz 3 \
-prefix ${img}.atlas_motionINT_EPIxEPI1.nii.gz

# method 3
cat_matvec -ONELINE \
mprage.noskull_at.nii.gz::WARP_DATA -I \
${EPIREF}.mprage.noskull_obla2e_mat.1D \
${EPIREF}.mprage.noskull_e2a_only_mat.aff12.1D -I \
${img}.motion_REF-INT.aff12.1D \
> ${img}.XFM.EPI2EPI2MPR2ATL_motionINT_EPIxMPR.aff12.1D

3dAllineate \
-overwrite \
-base mprage.noskull_at.nii.gz \
-input ${img}.nii.gz \
-1Dmatrix_apply ${img}.XFM.EPI2EPI2MPR2ATL_motionINT_EPIxMPR.aff12.1D \
-mast_dxyz 3 \
-prefix ${img}.atlas_motionINT_EPIxMPR.nii.gz

# if the first (raw) image
endif

# if not the first run
endif

# end image loop
end

# create motion corrected then tshifted images, copy appropriate motion transforms
if ( ${runslicetime} == 'nogo' ) then
echo WARNING No need to slice time correct or the slice timing is unspecified
cp pb01.${sub}.rest${run}.tcat.atlas.nii.gz pb06.${sub}.rest${run}.tcat.atlas.tshift.nii.gz
else
3dTshift -ignore ${ignorefr} -tzero 0 -tpattern ${runslicetime} -heptic -prefix pb06.${sub}.rest${run}.tcat.atlas.tshift.nii.gz pb01.${sub}.rest${run}.tcat.atlas.nii.gz
endif
cp pb01.${sub}.rest${run}.tcat.motion.motion_bef_volreg.1D pb06.${sub}.rest${run}.tcat.atlas.tshift.motion_bef_volreg.1D
if ( ${runslicetime} == 'nogo' ) then
echo WARNING No need to slice time correct or the slice timing is unspecified
cp pb02.${sub}.rest${run}.despike.atlas.nii.gz pb07.${sub}.rest${run}.despike.atlas.tshift.nii.gz
else
3dTshift -ignore ${ignorefr} -tzero 0 -tpattern ${runslicetime} -heptic -prefix pb07.${sub}.rest${run}.despike.atlas.tshift.nii.gz pb02.${sub}.rest${run}.despike.atlas.nii.gz
cp pb02.${sub}.rest${run}.despike.motion.motion_bef_volreg.1D pb07.${sub}.rest${run}.despike.atlas.tshift.motion_bef_volreg.1D
endif
# end run loop
end


echo ----------------------------------------------------------
echo ----------------------------------------------------------
echo CREATE MASKS FROM FREESURFER SEGMENTATION
echo ----------------------------------------------------------
echo ----------------------------------------------------------

# copy in the FreeSurfer segmentation and transform it to atlas space
mri_convert ${FSdir}/mri/aparc+aseg.mgz ./aparc+aseg.nii.gz

cat_matvec -ONELINE \
mprage.noskull_at.nii.gz::WARP_DATA -I \
FSorig.XFM.FS2MPR.aff12.1D > aparc+aseg.XFM.FS2MPR2ATL.aff12.1D

# create atlas-aligned version of aparc+aseg
3dAllineate \
-final NN \
-1Dmatrix_apply aparc+aseg.XFM.FS2MPR2ATL.aff12.1D \
-prefix aparc+aseg.atlas.nii.gz \
-base mprage.noskull_at.nii.gz \
-input aparc+aseg.nii.gz \
-overwrite \
-nopad

# extract the GM, WM, CSF, and WB compartments

# everything labeled in FS, followed by resampling to the BOLD resolution
3dcalc -a aparc+aseg.atlas.nii.gz \
-expr 'not(equals(a,0))' \
-prefix aparc+aseg.atlas.INBRAINMASK_ero0.nii.gz

3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas.INBRAINMASK_ero0_EPI.nii.gz -inset aparc+aseg.atlas.INBRAINMASK_ero0.nii.gz

# the major WM compartments, with 4 erosions at the T1 resolution followed by resampling to the BOLD resolution
3dcalc -a aparc+aseg.atlas.nii.gz \
-expr 'equals(a,2)+equals(a,7)+equals(a,41)+equals(a,46)+equals(a,251)+equals(a,252)+equals(a,253)+equals(a,254)+equals(a,255)' \
-prefix aparc+aseg.atlas.WMMASK_ero0.nii.gz

3dcalc -a aparc+aseg.atlas.WMMASK_ero0.nii.gz -b a+i -c a-i -d a+j -e a-j -f a+k -g a-k \
-expr 'a*(1-amongst(0,b,c,d,e,f,g))' \
-prefix aparc+aseg.atlas.WMMASK_ero1.nii.gz

3dcalc -a aparc+aseg.atlas.WMMASK_ero1.nii.gz -b a+i -c a-i -d a+j -e a-j -f a+k -g a-k \
-expr 'a*(1-amongst(0,b,c,d,e,f,g))' \
-prefix aparc+aseg.atlas.WMMASK_ero2.nii.gz

3dcalc -a aparc+aseg.atlas.WMMASK_ero2.nii.gz -b a+i -c a-i -d a+j -e a-j -f a+k -g a-k \
-expr 'a*(1-amongst(0,b,c,d,e,f,g))' \
-prefix aparc+aseg.atlas.WMMASK_ero3.nii.gz

3dcalc -a aparc+aseg.atlas.WMMASK_ero3.nii.gz -b a+i -c a-i -d a+j -e a-j -f a+k -g a-k \
-expr 'a*(1-amongst(0,b,c,d,e,f,g))' \
-prefix aparc+aseg.atlas.WMMASK_ero4.nii.gz

3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas.WMMASK_ero0_EPI.nii.gz -inset aparc+aseg.atlas.WMMASK_ero0.nii.gz
3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas.WMMASK_ero1_EPI.nii.gz -inset aparc+aseg.atlas.WMMASK_ero1.nii.gz
3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas.WMMASK_ero2_EPI.nii.gz -inset aparc+aseg.atlas.WMMASK_ero2.nii.gz
3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas.WMMASK_ero3_EPI.nii.gz -inset aparc+aseg.atlas.WMMASK_ero3.nii.gz
3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas.WMMASK_ero4_EPI.nii.gz -inset aparc+aseg.atlas.WMMASK_ero4.nii.gz

# the major CSF compartments, with 4 erosions at the T1 resolution followed by resampling to the BOLD resolution
3dcalc -a aparc+aseg.atlas.nii.gz \
-expr 'equals(a,4)+equals(a,43)+equals(a,14)' \
-prefix aparc+aseg.atlas.CSFMASK_ero0.nii.gz

3dcalc -a aparc+aseg.atlas.CSFMASK_ero0.nii.gz -b a+i -c a-i -d a+j -e a-j -f a+k -g a-k \
-expr 'a*(1-amongst(0,b,c,d,e,f,g))' \
-prefix aparc+aseg.atlas.CSFMASK_ero1.nii.gz

3dcalc -a aparc+aseg.atlas.CSFMASK_ero1.nii.gz -b a+i -c a-i -d a+j -e a-j -f a+k -g a-k \
-expr 'a*(1-amongst(0,b,c,d,e,f,g))' \
-prefix aparc+aseg.atlas.CSFMASK_ero2.nii.gz

3dcalc -a aparc+aseg.atlas.CSFMASK_ero2.nii.gz -b a+i -c a-i -d a+j -e a-j -f a+k -g a-k \
-expr 'a*(1-amongst(0,b,c,d,e,f,g))' \
-prefix aparc+aseg.atlas.CSFMASK_ero3.nii.gz

3dcalc -a aparc+aseg.atlas.CSFMASK_ero3.nii.gz -b a+i -c a-i -d a+j -e a-j -f a+k -g a-k \
-expr 'a*(1-amongst(0,b,c,d,e,f,g))' \
-prefix aparc+aseg.atlas.CSFMASK_ero4.nii.gz

3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas.CSFMASK_ero0_EPI.nii.gz -inset aparc+aseg.atlas.CSFMASK_ero0.nii.gz
3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas.CSFMASK_ero1_EPI.nii.gz -inset aparc+aseg.atlas.CSFMASK_ero1.nii.gz
3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas.CSFMASK_ero2_EPI.nii.gz -inset aparc+aseg.atlas.CSFMASK_ero2.nii.gz
3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas.CSFMASK_ero3_EPI.nii.gz -inset aparc+aseg.atlas.CSFMASK_ero3.nii.gz
3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas.CSFMASK_ero4_EPI.nii.gz -inset aparc+aseg.atlas.CSFMASK_ero4.nii.gz

# the gray matter ribbon (amygdala and hippocampus need to be added - 17 18 53 54
3dcalc -a aparc+aseg.atlas.nii.gz \
-expr 'within(a,1000,3000)+equals(a,17)+equals(a,18)+equals(a,53)+equals(a,54)' \
-prefix aparc+aseg.atlas.GM_RIBBONMASK_ero0.nii.gz


3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas.GM_RIBBONMASK_ero0_EPI.nii.gz -inset aparc+aseg.atlas.GM_RIBBONMASK_ero0.nii.gz

# the cerebellum
3dcalc -a aparc+aseg.atlas.nii.gz \
-expr 'equals(a,47)+equals(a,8)' \
-prefix aparc+aseg.atlas.GM_CBLMMASK_ero0.nii.gz

3dcalc -a aparc+aseg.atlas.GM_CBLMMASK_ero0.nii.gz -b a+i -c a-i -d a+j -e a-j -f a+k -g a-k \
-expr 'a*(1-amongst(0,b,c,d,e,f,g))' \
-prefix aparc+aseg.atlas.GM_CBLMMASK_ero1.nii.gz

3dcalc -a aparc+aseg.atlas.GM_CBLMMASK_ero1.nii.gz -b a+i -c a-i -d a+j -e a-j -f a+k -g a-k \
-expr 'a*(1-amongst(0,b,c,d,e,f,g))' \
-prefix aparc+aseg.atlas.GM_CBLMMASK_ero2.nii.gz

3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas.GM_CBLMMASK_ero0_EPI.nii.gz -inset aparc+aseg.atlas.GM_CBLMMASK_ero0.nii.gz
3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas.GM_CBLMMASK_ero1_EPI.nii.gz -inset aparc+aseg.atlas.GM_CBLMMASK_ero1.nii.gz
3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas.GM_CBLMMASK_ero2_EPI.nii.gz -inset aparc+aseg.atlas.GM_CBLMMASK_ero2.nii.gz

# the subcortical nuclei
3dcalc -a aparc+aseg.atlas.nii.gz \
-expr 'equals(a,11)+equals(a,12)+equals(a,10)+equals(a,49)+equals(a,50)+equals(a,51)' \
-prefix aparc+aseg.atlas.GM_SCMASK_ero0.nii.gz

3dcalc -a aparc+aseg.atlas.GM_SCMASK_ero0.nii.gz -b a+i -c a-i -d a+j -e a-j -f a+k -g a-k \
-expr 'a*(1-amongst(0,b,c,d,e,f,g))' \
-prefix aparc+aseg.atlas.GM_SCMASK_ero1.nii.gz

3dcalc -a aparc+aseg.atlas.GM_SCMASK_ero1.nii.gz -b a+i -c a-i -d a+j -e a-j -f a+k -g a-k \
-expr 'a*(1-amongst(0,b,c,d,e,f,g))' \
-prefix aparc+aseg.atlas.GM_SCMASK_ero2.nii.gz

3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas.GM_SCMASK_ero0_EPI.nii.gz -inset aparc+aseg.atlas.GM_SCMASK_ero0.nii.gz
3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas.GM_SCMASK_ero1_EPI.nii.gz -inset aparc+aseg.atlas.GM_SCMASK_ero1.nii.gz
3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas.GM_SCMASK_ero2_EPI.nii.gz -inset aparc+aseg.atlas.GM_SCMASK_ero2.nii.gz

# all gray matter
3dcalc -a aparc+aseg.atlas.nii.gz \
-expr 'within(a,1000,3000)+equals(a,17)+equals(a,18)+equals(a,53)+equals(a,54)+equals(a,47)+equals(a,8)+equals(a,11)+equals(a,12)+equals(a,10)+equals(a,49)+equals(a,50)+equals(a,51)' \
-prefix aparc+aseg.atlas.GM_ALLMASK_ero0.nii.gz

3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas.GM_ALLMASK_ero0_EPI.nii.gz -inset aparc+aseg.atlas.GM_ALLMASK_ero0.nii.gz

# and finally create images of the TT_N27 atlas and the MPRAGE and the FS segmentation, resampled to BOLD resolution
cp ${scriptdir}/TT_N27.nii.gz .
3dresample -rmode Li -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix TT_N27_EPI.nii.gz -inset TT_N27.nii.gz
3dresample -rmode Li -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix mprage_at_EPI.nii.gz -inset mprage_at.nii.gz
3dresample -rmode Li -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix mprage.noskull_at_EPI.nii.gz -inset mprage.noskull_at.nii.gz
3dresample -rmode NN -master pb01.${sub}.rest${firstRun}.tcat.atlas.nii.gz -prefix aparc+aseg.atlas_EPI.nii.gz -inset aparc+aseg.atlas.nii.gz



echo ----------------------------------------------------------
echo ----------------------------------------------------------
echo COMPUTE DVARS, STDEV, MEAN across each functional image
echo ----------------------------------------------------------
echo ----------------------------------------------------------

set boldimgs = `ls pb*.nii.gz | grep -v tcat4 | grep -v SPIKES`
foreach img ( ${boldimgs} )
echo Obtaining desciptors for ${img}
set imgstem = `echo $img | sed 's/\(.*\)\.\(.*\)\.\(.*\)/\1/g'`
${scriptdir}/calcDVARS.sh ${imgstem}.nii.gz ${imgstem}.DVARS.txt
${scriptdir}/calcMEANS.sh ${imgstem}.nii.gz ${imgstem}.MEANS.txt
${scriptdir}/calcSTDEV.sh ${imgstem}.nii.gz ${imgstem}.STDEV.txt
end
