#!/bin/bash
#
#SBATCH --job-name=imfse
#SBATCH --ntasks-per-node=1
#SBATCH -p prod
#SBATCH --mem 90
#
source /opt/intel/oneapi/setvars.sh 
export OMP_NUM_THREADS=1
cd SLURM_SUBMIT_DIR
mpirun -np $SLURM_NTASKS  /opt/FDS/Build/fds_impi_intel_linux_openmp_db input_steckler.fds
