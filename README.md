# Full-text-Scaling
Files related to the scaling of the full legislative tests to be stored here


### Dependencies
**GPU REQUIRED**
Install CUDA from https://developer.nvidia.com/cuda-downloads

Install the following python modules using pip or conda:

- Python >= 3.6 
- Pandas
- nltk
- traceback
- huggingface transformers
- huggingface datasets
- statistics 

### Instructions
This repository contains code for running full-text scaling. Following are the steps to run the full-text scaling.

1.  First, we need alignments. **Alignment** is basically matches and mismatches computed between proposal-trilogues-final act. Alignments are done in 3 steps within the `alignment.py` file. To run the alignment file, kindly provide the path for variables `trilog_base_path` which is the path of trilogues in csv format, `proposal_alignment_path` where proposal-trilog alignment will be stored, `df_prop_full` where the full proposal text in csv format is present, `alignment_path` where the final alignments will be stored, and `df_final_full` path where the final text is present in csv format. After providing paths, run the command `CUDA_VISIBLE_DEVICES=<GPU-ID> python alignment.py`
2.  Now we run the scaling. Provide model path for classification in the `model_base_path` variable. Furthermore, provide paths to proposal text in the variable 'data_base_path' and write path variable `write_base_path`. Run the command `CUDA_VISIBLE_DEVICES=<GPU-ID> python scaling_prop.py`. After, running the proposal scaling, repeat the above steps for final text scaling and then run the command `CUDA_VISIBLE_DEVICES=<GPU-ID> python scaling_final.py`. Final scaling will be making use of the proposal scaling output.
3.  Lastly, combine all the results of scaling in one single .csv file using. Provide path to `data_base_path` and `write_base_path`, and then run the command `python combine_files.py`.

If there are any problems, kindly open an issue. 

