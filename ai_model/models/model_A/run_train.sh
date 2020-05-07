#!/bin/bash

### User define parameters
model_name_or_path=bert-base-chinese
data_dir=./data/
output_dir=models_bert/

learning_rate=1e-4
num_train_epochs=1
max_seq_length=128
per_gpu_eval_batch_size=16
per_gpu_train_batch_size=16
gradient_accumulation_steps=2

### run training program
python ./run_multi_label_classification.py \
--task_name cofacts \
--model_name_or_path $model_name_or_path \
--do_train \
--do_eval \
--data_dir $data_dir \
--learning_rate $learning_rate \
--num_train_epochs $num_train_epochs \
--max_seq_length $max_seq_length \
--output_dir $output_dir \
--per_gpu_eval_batch_size=$per_gpu_eval_batch_size \
--per_gpu_train_batch_size=$per_gpu_train_batch_size \
--gradient_accumulation_steps $gradient_accumulation_steps \
--overwrite_output
